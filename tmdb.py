"""TMDB API client for live movie discovery."""
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from constants import IMAGE_BASE_URL

load_dotenv()
def _secret_or_env(name):
    value = os.getenv(name, "")
    try:
        value = value or st.secrets.get(name, "")
    except Exception:
        pass
    return str(value).strip().strip('"').strip("'")

API_KEY = _secret_or_env("TMDB_API_KEY")
ACCESS_TOKEN = _secret_or_env("TMDB_READ_ACCESS_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"
REGION = os.getenv("TMDB_REGION", "IN").strip().upper() or "IN"
LANGUAGE = os.getenv("TMDB_LANGUAGE", "en-US").strip() or "en-US"
session = requests.Session()
session.headers.update({"User-Agent": "CineMatch/2.0 (Streamlit movie discovery app)"})

def _get(path, params=None):
    if not (ACCESS_TOKEN or API_KEY):
        raise RuntimeError("TMDB credentials missing. Add TMDB_API_KEY or TMDB_READ_ACCESS_TOKEN to .env / Streamlit secrets.")
    query = dict(params or {})
    query.setdefault("language", LANGUAGE)
    headers = {}
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    else:
        query["api_key"] = API_KEY
    response = session.get(f"{BASE_URL}/{path.lstrip('/')}", params=query, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json()

def poster_url(path, size="w500"):
    return f"https://image.tmdb.org/t/p/{size}{path}" if path else None

@st.cache_data(ttl=1800, show_spinner=False)
def get_movie_list(category="trending", page=1, region=REGION):
    params = {"page": page}
    if category == "trending": data = _get("trending/movie/week", params)
    elif category == "popular": data = _get("movie/popular", params)
    elif category == "upcoming": data = _get("movie/upcoming", {**params, "region": region})
    elif category == "now_playing": data = _get("movie/now_playing", {**params, "region": region})
    elif category == "top_rated": data = _get("movie/top_rated", params)
    else: raise ValueError(f"Unsupported movie category: {category}")
    return data.get("results", [])

@st.cache_data(ttl=1800, show_spinner=False)
def get_upcoming_page(page=1, region=REGION):
    """Fetch one page of upcoming releases plus TMDB pagination metadata.

    Passing an empty region asks TMDB for its unfiltered upcoming catalogue.
    TMDB paginates results; the UI lets users browse every returned page.
    """
    params = {"page": max(1, int(page))}
    if region:
        params["region"] = region
    data = _get("movie/upcoming", params)
    return {
        "results": data.get("results", []),
        "page": data.get("page", page),
        "total_pages": min(int(data.get("total_pages", 1) or 1), 500),
        "total_results": int(data.get("total_results", 0) or 0),
    }


@st.cache_data(ttl=900, show_spinner=False)
def search_movies(query, page=1):
    if not query or not query.strip(): return []
    return _get("search/movie", {"query": query.strip(), "page": page, "include_adult": "false"}).get("results", [])

@st.cache_data(ttl=3600, show_spinner=False)
def get_movie_details(movie_id):
    return _get(f"movie/{int(movie_id)}", {"append_to_response": "videos,credits"})

@st.cache_data(ttl=3600, show_spinner=False)
def get_live_recommendations(movie_id):
    return _get(f"movie/{int(movie_id)}/recommendations").get("results", [])

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_poster(movie_id):
    try: return poster_url(_get(f"movie/{int(movie_id)}").get("poster_path"))
    except (requests.RequestException, RuntimeError, ValueError): return None


def enrich_movie_metadata(movie_id=None, title=None, release_date=None):
    """Resolve poster/rating/date metadata for an ML candidate using live TMDB."""
    data = {}
    if movie_id is not None:
        try:
            data = _get(f"movie/{int(movie_id)}")
        except (requests.RequestException, RuntimeError, ValueError, TypeError):
            data = {}
    if not data.get("poster_path") and title:
        try:
            matches = search_movies(str(title))
            if release_date:
                year = str(release_date)[:4]
                matches = sorted(matches, key=lambda item: 0 if str(item.get("release_date", "")).startswith(year) else 1)
            if matches:
                # Prefer non-empty detail values, but preserve poster/rating/date from
                # search results when the details endpoint has null/empty fields.
                search_match = matches[0]
                merged = dict(search_match)
                for key, value in data.items():
                    if value not in (None, ""):
                        merged[key] = value
                data = merged
        except (requests.RequestException, RuntimeError, ValueError):
            pass
    return {
        "poster_url": poster_url(data.get("poster_path")),
        "poster_path": data.get("poster_path"),
        "vote_average": data.get("vote_average"),
        "release_date": data.get("release_date") or release_date or "",
        "overview": data.get("overview", ""),
    }
