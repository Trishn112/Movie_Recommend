import os
import requests
import streamlit as st
from dotenv import load_dotenv
from constants import IMAGE_BASE_URL, TMDB_MOVIE_URL

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

session = requests.Session()


@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):

    url = f"{TMDB_MOVIE_URL}{movie_id}?api_key={API_KEY}"

    try:

        response = session.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        poster = data.get("poster_path")

        if poster:
            return IMAGE_BASE_URL + poster

        return None

    except requests.exceptions.RequestException as e:

        print(f"TMDB Error ({movie_id}):", e)

        return None