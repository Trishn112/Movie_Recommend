"""Load original pickle artifacts when present; otherwise rebuild from included TMDB CSVs."""
import ast, pickle
from pathlib import Path
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
BASE=Path(__file__).resolve().parent
MOVIE_FILE, SIM_FILE = BASE/"movie.pkl", BASE/"sim.pkl"
MOVIES_CSV, CREDITS_CSV = BASE/"tmdb_5000_movies.csv", BASE/"tmdb_5000_credits.csv"

def _lfs_pointer(path):
    try:
        with path.open("rb") as f: return f.read(80).startswith(b"version https://git-lfs.github.com/spec/v1")
    except OSError: return True

def _names(value, limit=None):
    try:
        vals=[str(x.get("name","")) for x in ast.literal_eval(value) if isinstance(x,dict)]
        return vals[:limit] if limit else vals
    except (ValueError,SyntaxError,TypeError): return []

@st.cache_resource(show_spinner="Preparing CineMatch content model from TMDB 5000...")
def _build_fallback():
    if not MOVIES_CSV.exists() or not CREDITS_CSV.exists():
        raise FileNotFoundError("Original pickle artifacts unavailable and TMDB 5000 CSV files are missing.")
    movies=pd.read_csv(MOVIES_CSV)
    credits=pd.read_csv(CREDITS_CSV).drop_duplicates(subset=["title"])
    data=movies.merge(credits,on="title",how="inner",suffixes=("","_credits"))
    data=data.dropna(subset=["overview","title"]).copy()
    data["genres_text"]=data["genres"].apply(_names)
    data["keywords_text"]=data["keywords"].apply(_names)
    data["cast_text"]=data["cast"].apply(lambda x:_names(x,3))
    def director(value):
        try:
            for p in ast.literal_eval(value):
                if p.get("job")=="Director": return p.get("name","")
        except (ValueError,SyntaxError,TypeError): pass
        return ""
    data["director_text"]=data["crew"].apply(director)
    data["tags"]=(data["overview"].fillna("")+" "+data["genres_text"].apply(" ".join)+" "+data["keywords_text"].apply(" ".join)+" "+data["cast_text"].apply(" ".join)+" "+data["director_text"]).str.lower()
    vectors=CountVectorizer(max_features=5000,stop_words="english").fit_transform(data["tags"])
    similarity=cosine_similarity(vectors,dense_output=False)
    data=data.rename(columns={"id":"movie_id"}).reset_index(drop=True)
    return data,similarity

@st.cache_resource(show_spinner="Loading CineMatch recommendation model...")
def load_data():
    if MOVIE_FILE.exists() and SIM_FILE.exists() and not _lfs_pointer(MOVIE_FILE) and not _lfs_pointer(SIM_FILE):
        try:
            with MOVIE_FILE.open("rb") as f: movies=pickle.load(f)
            with SIM_FILE.open("rb") as f: similarity=pickle.load(f)
            if len(movies)==similarity.shape[0]: return movies,similarity
        except Exception as exc: st.warning(f"Original pickle files could not be loaded ({exc}); using CSV fallback.")
    elif MOVIE_FILE.exists() and _lfs_pointer(MOVIE_FILE):
        st.info("Git LFS pointer found for movie.pkl. Rebuilding the content model from the included TMDB 5000 CSV files; original artifacts are not overwritten.")
    return _build_fallback()
