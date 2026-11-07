import streamlit as st
from tmdb import poster_url, enrich_movie_metadata

def _poster_for(movie):
    # TMDB's image URL requires the leading slash in poster_path.
    path = movie.get("poster_path")
    if path:
        return poster_url(path)
    existing = movie.get("poster_url")
    if existing:
        return existing
    movie_id = movie.get("id") or movie.get("movie_id")
    title = movie.get("title") or movie.get("name")
    try:
        metadata = enrich_movie_metadata(movie_id=movie_id, title=title,
                                         release_date=movie.get("release_date"))
        return metadata.get("poster_url")
    except Exception:
        return None

def show_movies(names, posters):
    cols = st.columns(5)
    for i, (name, poster) in enumerate(zip(names, posters)):
        with cols[i % 5]:
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.info("Poster unavailable")
            st.markdown(f'<div class="movie-card"><div class="movie-title">{name}</div></div>',
                        unsafe_allow_html=True)

def show_live_movies(movies, key_prefix="live", columns=5):
    if not movies:
        st.info("No movies found for this section.")
        return
    cols = st.columns(columns)
    for i, movie in enumerate(movies):
        with cols[i % columns]:
            image = _poster_for(movie)
            if image:
                st.image(image, use_container_width=True)
            else:
                st.info("Poster not provided by TMDB")
            title = movie.get("title") or movie.get("name") or "Untitled"
            date = movie.get("release_date") or "Release date unavailable"
            rating = movie.get("vote_average")
            rating_text = f"⭐ {float(rating):.1f}/10" if rating is not None else "Rating unavailable"
            st.markdown(
                f'<div class="movie-card"><div class="movie-title">{title}</div>'
                f'<p>{date}</p><p>{rating_text}</p></div>',
                unsafe_allow_html=True
            )
