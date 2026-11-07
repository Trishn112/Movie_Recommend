# CineMatch – Movie Recommendation System

CineMatch combines the original TMDB 5000 content-based recommendation model with live TMDB discovery.

## Features
- Original similarity recommendations for titles in the TMDB 5000 training set.
- Live weekly trending, popular, now-playing (India by default), and upcoming shelves.
- Search the TMDB catalogue, including new releases.
- TMDB recommendations for titles outside the original training set.
- Cached API responses to reduce repeated requests.

## Setup
1. Use Python 3.10–3.12.
2. Install: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your TMDB API key or Read Access Token.
4. Run: `streamlit run ui.py`

## Original model preservation
If valid `movie.pkl` and `sim.pkl` files exist, CineMatch loads them directly without modifying or retraining them. If the repository contains Git LFS pointer stubs or the similarity file is absent, the app rebuilds a sparse content-based model from the included TMDB 5000 CSV files. It does not overwrite the original pickle files.

## TMDB attribution
This product uses the TMDB API but is not endorsed or certified by TMDB.


## Upcoming catalogue
The Upcoming tab uses TMDB's paginated `/movie/upcoming` endpoint and exposes every page returned by TMDB (up to its API page limit), with India, US, UK, Canada, Australia, and unfiltered region choices. The month filter applies to the selected page; use the page selector or Previous/Next controls to browse the full result set. TMDB itself determines which movies count as upcoming and may not list every future film worldwide.

## Poster fallback
Poster paths from movie details and title search are merged without allowing null detail fields to overwrite valid search-result poster paths. When a recommendation candidate lacks a poster path, CineMatch looks up the title and release year through TMDB before showing a placeholder.
