import streamlit as st


def show_movies(names, posters):

    cols = st.columns(5)

    for i in range(len(names)):

        with cols[i]:

            if posters[i]:
                st.image(
                    posters[i],
                    use_container_width=True
                )
            else:
                st.info("No Poster")

            st.markdown(
                f"""
                <div class="movie-card">

                <div class="movie-title">
                {names[i]}
                </div>

                </div>
                """,
         unsafe_allow_html=True
        )