import pickle
import streamlit as st


@st.cache_data
def load_data():

    movies = pickle.load(open("movie.pkl", "rb"))
    similarity = pickle.load(open("sim.pkl", "rb"))

    return movies, similarity