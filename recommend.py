from tmdb import fetch_poster


def recommend_movie(movie, movies, similarity):

    movie = movie.lower().strip()

    index = movies[movies["title"].str.lower() == movie].index[0]

    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    # 👇 Add this here
    for i in movie_list:

        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title

        print(title, movie_id)

        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters