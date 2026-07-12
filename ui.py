import streamlit as st
from config import page_config
from style import load_css
from header import show_header
from data_loader import load_data
from recommend import recommend_movie
from cards import show_movies
page_config()
load_css()
show_header()
movies, similarity = load_data()
selected_movie = st.selectbox(
    "🎥 Select a Movie",
    movies["title"].values
)
st.write("")
if st.button("🍿 Recommend Movies"):
    with st.spinner("Finding similar movies..."):
        movie_names, posters = recommend_movie(
            selected_movie,
            movies,
            similarity
        )
    st.subheader("Recommended Movies")

    show_movies(movie_names, posters)
st.markdown("""
<div class="footer">

Built with ❤️ using Streamlit • Scikit-learn • TMDB API

</div>
""", unsafe_allow_html=True)