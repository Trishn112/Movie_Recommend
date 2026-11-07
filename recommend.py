"""Unified hybrid recommender: original CineMatch ML + live TMDB."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tmdb import fetch_poster, get_live_recommendations, get_movie_details, poster_url, enrich_movie_metadata


def _title_column(movies):
    return "title" if "title" in movies.columns else "original_title"


def _row_movie_id(row):
    value = row.get("movie_id", row.get("id"))
    try:
        return int(value) if pd.notna(value) else None
    except (TypeError, ValueError):
        return None


def _similarity_row(similarity, index):
    if hasattr(similarity, "getrow"):
        return similarity.getrow(index).toarray().ravel()
    return np.asarray(similarity[index]).ravel()


def _ml_candidates(title, movie_id, movies, similarity, limit=20):
    """Use original cosine matrix for known titles; content-vector bridge for new titles."""
    title_col = _title_column(movies)
    matches = pd.DataFrame()
    id_col = "movie_id" if "movie_id" in movies.columns else ("id" if "id" in movies.columns else None)
    if id_col:
        try:
            matches = movies[pd.to_numeric(movies[id_col], errors="coerce") == int(movie_id)]
        except (TypeError, ValueError):
            pass
    if matches.empty:
        matches = movies[movies[title_col].astype(str).str.casefold() == str(title).strip().casefold()]
    if not matches.empty and similarity is not None:
        # Use positional indexing so non-contiguous DataFrame labels cannot misalign the matrix.
        index = int(np.flatnonzero(movies.index.isin(matches.index))[0])
        scores = _similarity_row(similarity, index)
    else:
        index = -1
        # New release absent from TMDB 5000: transform its live metadata into the
        # same bag-of-words content space and compare it with the original corpus.
        scores = _score_external_movie(movie_id, movies)
        if scores is None:
            return []
    ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
    output = []
    for row_index, score in ranked:
        if row_index == index:
            continue
        row = movies.iloc[row_index]
        movie_id = _row_movie_id(row)
        candidate_title = str(row.get(title_col, "Untitled"))
        candidate_date = str(row.get("release_date", "") or "")
        metadata = enrich_movie_metadata(movie_id, candidate_title, candidate_date) if movie_id else {}
        output.append({
            "id": movie_id,
            "title": candidate_title,
            "poster_url": metadata.get("poster_url") or (fetch_poster(movie_id) if movie_id else None),
            "poster_path": metadata.get("poster_path"),
            "vote_average": metadata.get("vote_average"),
            "release_date": metadata.get("release_date") or candidate_date,
            "overview": metadata.get("overview", ""),
            "_rank": len(output) + 1,
            "_raw_score": float(score),
            "_source": "CineMatch ML",
        })
        if len(output) >= limit:
            break
    return output


_CONTENT_SPACE_CACHE = {}


def _score_external_movie(movie_id, movies):
    """Project a live movie's metadata into the TMDB 5000 content feature space."""
    if "tags" not in movies.columns:
        return None
    tags = movies["tags"].fillna("").astype(str)
    if not tags.str.strip().any():
        return None
    cache_key = id(movies)
    if cache_key not in _CONTENT_SPACE_CACHE:
        vectorizer = CountVectorizer(max_features=5000, stop_words="english")
        matrix = vectorizer.fit_transform(tags)
        _CONTENT_SPACE_CACHE[cache_key] = (vectorizer, matrix)
    vectorizer, matrix = _CONTENT_SPACE_CACHE[cache_key]
    try:
        details = get_movie_details(movie_id)
    except Exception:
        return None
    parts = [details.get("overview", "")]
    parts.extend(g.get("name", "") for g in details.get("genres", []))
    keywords = details.get("keywords", {})
    parts.extend(k.get("name", "") for k in keywords.get("keywords", keywords.get("results", [])))
    credits = details.get("credits", {})
    parts.extend(c.get("name", "") for c in credits.get("cast", [])[:5])
    parts.extend(c.get("name", "") for c in credits.get("crew", []) if c.get("job") == "Director")
    query_vector = vectorizer.transform([" ".join(str(part) for part in parts)])
    return cosine_similarity(query_vector, matrix).ravel()


def _tmdb_candidates(movie_id, limit=30):
    """Fetch live recommendation candidates for any TMDB movie, including recent releases."""
    try:
        results = get_live_recommendations(movie_id)
    except Exception:
        results = []
    if not results:
        # TMDB's similar endpoint is a useful fallback for titles with no recommendation list.
        from tmdb import _get
        try:
            results = _get(f"movie/{int(movie_id)}/similar").get("results", [])
        except Exception:
            results = []
    candidates = []
    for item in results:
        if not item.get("id") or not item.get("title"):
            continue
        candidates.append({
            **item,
            "poster_url": poster_url(item.get("poster_path")),
            "_rank": len(candidates) + 1,
            "_source": "TMDB live",
        })
        if len(candidates) >= limit:
            break
    return candidates


def hybrid_recommendations(movie_id, title, movies, similarity, limit=12,
                           ml_weight=0.55, tmdb_weight=0.45):
    """Merge both candidate pools, deduplicate, and rank with weighted reciprocal-rank fusion.

    Known TMDB 5000 titles benefit from both recommenders. Newer titles absent from
    the training set still receive live TMDB recommendations through this same API.
    """
    ml = _ml_candidates(title, movie_id, movies, similarity)
    live = _tmdb_candidates(movie_id)
    combined = {}

    def identity(item):
        if item.get("id") is not None:
            return f"id:{item['id']}"
        return "title:" + str(item.get("title", "")).casefold().strip()

    for pool, weight, source in ((ml, ml_weight, "CineMatch ML"), (live, tmdb_weight, "TMDB live")):
        for item in pool:
            key = identity(item)
            if key not in combined:
                combined[key] = dict(item, _hybrid_score=0.0, _sources=[])
            target = combined[key]
            rank = max(1, int(item.get("_rank", 1)))
            target["_hybrid_score"] += weight / (60.0 + rank)
            if source not in target["_sources"]:
                target["_sources"].append(source)
            # Prefer live metadata/posters when the same movie appears in both pools.
            for field in ("poster_url", "poster_path", "vote_average", "release_date", "overview"):
                if item.get(field) not in (None, ""):
                    target[field] = item[field]

    ranked = sorted(combined.values(), key=lambda item: item["_hybrid_score"], reverse=True)
    results = []
    for item in ranked:
        item["source"] = " + ".join(item.pop("_sources", []))
        item.pop("_rank", None)
        item.pop("_raw_score", None)
        item.pop("_source", None)
        item.pop("_hybrid_score", None)
        results.append(item)
        if len(results) >= limit:
            break
    return results


# Backwards-compatible helpers retained for any older imports.
def recommend_movie(movie, movies, similarity, limit=5):
    candidates = _ml_candidates(movie, None, movies, similarity, limit)
    return [item["title"] for item in candidates], [item.get("poster_url") for item in candidates]


def recommend_live_movie(movie_id, limit=10):
    return _tmdb_candidates(movie_id, limit)
