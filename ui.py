import os
import streamlit as st
from config import page_config
from style import load_css
from header import show_header
from data_loader import load_data
from recommend import hybrid_recommendations
from cards import show_movies, show_live_movies
from tmdb import get_movie_list, get_upcoming_page, search_movies

page_config(); load_css(); show_header()
try: movies,similarity=load_data()
except Exception as exc: st.error(f"Could not load CineMatch model: {exc}"); st.stop()
st.caption("Original TMDB 5000 ML recommendations + live TMDB movie discovery.")
tabs=st.tabs(["🎯 Recommendations","🔥 Trending","⭐ Popular","🎬 Now Playing","🗓️ Upcoming","🔎 Search"])
with tabs[0]:
    st.subheader("One recommendation engine for every movie")
    st.write("Search any title.")
    query = st.text_input("Search a movie", placeholder="e.g. Inception, Dune: Part Two, or a 2026 release", key="hybrid_movie_search")
    if query:
        try:
            results = search_movies(query)
            if results:
                choices = {
                    f"{m.get('title')} ({(m.get('release_date') or 'date unknown')[:4]})": m
                    for m in results
                }
                label = st.selectbox("Select the movie", list(choices.keys()), key="hybrid_movie_choice")
                chosen = choices[label]
                if st.button("🍿 Get hybrid recommendations", key="hybrid_recommend_button"):
                    with st.spinner("Combining CineMatch ML and live TMDB recommendations..."):
                        recommendations = hybrid_recommendations(
                            chosen["id"], chosen.get("title", query), movies, similarity, limit=12
                        )
                    st.subheader(f"Because you selected {chosen.get('title')}")
                    if recommendations:
                        show_live_movies(recommendations, "hybrid_result")
                    else:
                        st.info("No recommendations were returned for this title yet.")
            else:
                st.info("No matching movies found in TMDB.")
        except Exception as exc:
            st.error(f"Could not create recommendations: {exc}")
    else:
        st.info("The ML model is preserved for titles in the original.")

def live_tab(tab,category,heading):
    with tab:
        st.subheader(heading)
        try:
            with st.spinner("Fetching the latest movies from TMDB..."):
                items=get_movie_list(category,region=os.getenv("TMDB_REGION","IN"))
            show_live_movies(items,category)
        except Exception as exc:
            st.error(f"Could not load {heading.lower()}: {exc}")
            st.caption("Check your TMDB credentials in .env or Streamlit secrets.")
live_tab(tabs[1],"trending","Trending This Week")
live_tab(tabs[2],"popular","Popular Movies")
live_tab(tabs[3],"now_playing","Now Playing in Your Region")
with tabs[4]:
    st.subheader("Upcoming Movies — Browse the full TMDB catalogue")
    st.write("Browse upcoming releases page by page, filter by release month, and open any movie poster/card.")

    region_options = {
        "India": "IN",
        "United States": "US",
        "United Kingdom": "GB",
        "Canada": "CA",
        "Australia": "AU",
        "All regions (unfiltered)": "",
    }
    region_label = st.selectbox("Release region", list(region_options.keys()), index=0,
                                key="upcoming_region")
    region_code = region_options[region_label]

    try:
        # Load page 1 first to learn the full result count and page count.
        with st.spinner("Loading upcoming movie catalogue..."):
            first_page = get_upcoming_page(1, region_code)
        total_pages = max(1, first_page["total_pages"])
        total_results = first_page["total_results"]
        st.caption(f"TMDB reports {total_results:,} upcoming movie entries across {total_pages:,} pages for {region_label}.")

        page = st.number_input("Catalogue page", min_value=1, max_value=total_pages,
                               value=1, step=1, key=f"upcoming_page_{region_code or 'all'}")
        page = int(page)
        with st.spinner(f"Loading upcoming movies — page {page} of {total_pages}..."):
            page_data = first_page if page == 1 else get_upcoming_page(page, region_code)
        page_movies = page_data["results"]

        # Month filtering is applied to the current page so the user can browse all
        # TMDB pages without silently truncating the catalogue to the first few pages.
        available_months = sorted({
            str(movie.get("release_date", ""))[:7]
            for movie in page_movies
            if len(str(movie.get("release_date", ""))) >= 7
        })
        month_labels = {"All release months": ""}
        for month_value in available_months:
            try:
                from datetime import datetime
                month_labels[datetime.strptime(month_value, "%Y-%m").strftime("%B %Y")] = month_value
            except ValueError:
                pass
        selected_month_label = st.selectbox("Filter this page by release month",
                                            list(month_labels.keys()),
                                            key=f"upcoming_month_{region_code or 'all'}_{page}")
        selected_month = month_labels[selected_month_label]
        visible_movies = [
            movie for movie in page_movies
            if not selected_month or str(movie.get("release_date", "")).startswith(selected_month)
        ]

        if selected_month:
            st.caption(f"Showing {len(visible_movies)} releases in {selected_month_label} on this page.")
        else:
            st.caption(f"Showing {len(visible_movies)} movies from page {page}.")

        if visible_movies:
            show_live_movies(visible_movies, f"upcoming_{region_code or 'all'}_{page}")
        else:
            st.info("No movies match this month on the selected page. Try another page or choose all months.")

        left, right = st.columns(2)
        with left:
            if page > 1 and st.button("← Previous page", key=f"upcoming_prev_{region_code or 'all'}"):
                st.session_state[f"upcoming_page_{region_code or 'all'}"] = page - 1
                st.rerun()
        with right:
            if page < total_pages and st.button("Next page →", key=f"upcoming_next_{region_code or 'all'}"):
                st.session_state[f"upcoming_page_{region_code or 'all'}"] = page + 1
                st.rerun()

        st.caption("TMDB provides a paginated upcoming catalogue. Some titles may not have posters or confirmed release dates yet.")
    except Exception as exc:
        st.error(f"Could not load upcoming movies: {exc}")
        st.caption("Check your TMDB credentials in .env or Streamlit secrets.")

with tabs[5]:
    st.subheader("Search the TMDB catalogue")
    query=st.text_input("Movie name",placeholder="Search any movie, old or new",key="catalog_search")
    if query:
        try: show_live_movies(search_movies(query),"search_result")
        except Exception as exc: st.error(f"Search failed: {exc}")
st.markdown("""<div class="footer">Built with ❤️ using Streamlit • Scikit-learn • TMDB API<br>Movie metadata and images provided by TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.</div>""",unsafe_allow_html=True)
