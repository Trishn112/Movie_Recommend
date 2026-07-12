import streamlit as st

def show_header():

    st.markdown(
    """
    <div class="hero">
        <h1> CineMatch</h1>
        <h3>Movie Recommendation System</h3>
        <p>
            Discover movies you'll love using
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.markdown("<br>", unsafe_allow_html=True)