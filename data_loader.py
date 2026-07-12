import os
import pickle
import gdown
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

SIM_FILE = "sim.pkl"
FILE_ID = os.getenv("FILE_ID") 

URL = f"https://drive.google.com/uc?id={FILE_ID}"

@st.cache_resource
def load_data():
    if not os.path.exists(SIM_FILE):
        print("Downloading similarity matrix...")
        gdown.download(URL, SIM_FILE, quiet=False)

    movies = pickle.load(open("movie.pkl", "rb"))
    similarity = pickle.load(open(SIM_FILE, "rb"))

    return movies, similarity