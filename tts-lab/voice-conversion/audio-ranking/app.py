import os
from io import BytesIO

import psycopg2
import requests
import streamlit as st
import streamlit_google_oauth as oauth
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]


# Function to insert data into the PostgreSQL database
def insert_ranking_data(conn, question_id, url, ranking, user_id):
    sql = "INSERT INTO audio_ranking (question_id, url, ranking, user_id) VALUES (%s, %s, %s, %s);"
    cur = conn.cursor()
    cur.execute(sql, (question_id, url, ranking, user_id))
    conn.commit()


def main():
    st.title("Audio Ranking")

    # Adding the guideline text
    st.write("In each question, there will be 4 audio files:")
    st.write("1. Three audio files from our models.")
    st.write("2. One audio file which is the true recording.")
    st.write("Please listen to all of them and then select the ranking.")
    st.write("1 means best, 4 means worst")
    st.write("Please select the ranking from top to bottom:")

    # Google Authentication
    st.subheader("Google Authentication")

    # Use st.session_state to store the authentication status
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Perform authentication step only if the user is not logged in
        if st.button("Authenticate"):
            try:
                login_info = oauth.login(
                    client_id=GOOGLE_CLIENT_ID,
                    client_secret=GOOGLE_CLIENT_SECRET,
                    redirect_uri=GOOGLE_REDIRECT_URI,
                    logout_button_text="Logout",
                )

                if login_info:
                    st.session_state.user_id = login_info[0]
                    st.session_state.authenticated = True

            except ValueError as e:
                st.error("Authentication failed")
                st.error(e)

        if not st.session_state.authenticated:
            st.warning("Please click 'Authenticate' to log in and proceed.")
            return

    # Initialize the rankings dictionary
    rankings = {}

    # Define audio data
    audio_data = {
        "urls": [
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0001.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0002.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0003.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0004.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0005.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0006.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0007.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0008.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0009.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0010.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0011.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0012.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0013.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0014.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0015.wav",
            "https://storage.googleapis.com/thaitang-sharing/audio-ranking/MBD1_KTXH_02_0016.wav",
        ],
    }

    urls = audio_data["urls"]
    num_blocks = len(urls) // 4

    # Connect to the PostgreSQL database using environment variables
    conn = psycopg2.connect(
        host=os.environ.get("DATABASE_HOST"),
        port=os.environ.get("DATABASE_PORT"),
        database=os.environ.get("DATABASE_NAME"),
        user=os.environ.get("DATABASE_USER"),
        password=os.environ.get("DATABASE_PASSWORD"),
    )

    for block in range(num_blocks):
        question_num = block + 1
        st.write(f"Question {question_num}")
        st.write("Rankings:")

        block_urls = urls[block * 4 : (block + 1) * 4]
        block_rankings = []

        for i, url in enumerate(block_urls):
            response = requests.get(url)
            audio_bytes = BytesIO(response.content)
            st.audio(audio_bytes, format="audio/wav")

            options = [1, 2, 3, 4]
            if i > 0:
                options = [
                    option
                    for option in options
                    if option not in block_rankings
                ]

            ranking = st.selectbox(
                f"Ranking for URL {i+1}:", options=options, key=url
            )
            block_rankings.append(ranking)

            # Persist data to PostgreSQL database
            insert_ranking_data(
                conn, question_num, url, ranking, st.session_state.user_id
            )

        if None not in block_rankings:
            rankings[f"Question {question_num}"] = block_rankings

        st.write("---")

    conn.close()


if __name__ == "__main__":
    main()
