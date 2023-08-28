import os
from io import BytesIO

import psycopg2
import streamlit as st
import streamlit_google_oauth as oauth
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]


# Define audios for scoring
audio_data = [
    {
        "question_id": "1",
        "paths": [
            "original/FGL1.KTXH_07_0016.wav",
            "stargan_best_x/FGL1.KTXH_07_0016.wav",
            "stargan_best_y/FGL1.KTXH_07_0016.wav",
        ],
    },
    {
        "question_id": "2",
        "paths": [
            "stargan_best_y/FGL1.KTXH_05_0006.wav",
            "stargan_best_x/FGL1.KTXH_05_0006.wav",
            "original/FGL1.KTXH_05_0006.wav",
        ],
    },
    {
        "question_id": "3",
        "paths": [
            "stargan_best_y/MGL1.KTXH_07_0016.wav",
            "original/MGL1.KTXH_07_0016.wav",
            "stargan_best_x/MGL1.KTXH_07_0016.wav",
        ],
    },
    {
        "question_id": "4",
        "paths": [
            "original/MKT1.TTCS_03_0001.wav",
            "stargan_best_x/MKT1.TTCS_03_0001.wav",
            "stargan_best_y/MKT1.TTCS_03_0001.wav",
        ],
    },
    {
        "question_id": "5",
        "paths": [
            "stargan_best_x/MKT1.TTCS_03_0003.wav",
            "stargan_best_y/MKT1.TTCS_03_0003.wav",
            "original/MKT1.TTCS_03_0003.wav",
        ],
    },
    {
        "question_id": "6",
        "paths": [
            "stargan_best_y/FBD1.KTXH_02_0001.wav",
            "original/FBD1.KTXH_02_0001.wav",
            "stargan_best_x/FBD1.KTXH_02_0001.wav",
        ],
    },
    {
        "question_id": "7",
        "paths": [
            "stargan_best_y/FKT1.TTCS_03_0001.wav",
            "stargan_best_x/FKT1.TTCS_03_0001.wav",
            "original/FKT1.TTCS_03_0001.wav",
        ],
    },
    {
        "question_id": "8",
        "paths": [
            "stargan_best_x/FBD1.KTXH_06_0002.wav",
            "original/FBD1.KTXH_06_0002.wav",
            "stargan_best_y/FBD1.KTXH_06_0002.wav",
        ],
    },
    {
        "question_id": "9",
        "paths": [
            "stargan_best_x/MKT1.TTCS_03_0004.wav",
            "stargan_best_y/MKT1.TTCS_03_0004.wav",
            "original/MKT1.TTCS_03_0004.wav",
        ],
    },
    {
        "question_id": "10",
        "paths": [
            "stargan_best_x/MKT1.TTCS_03_0002.wav",
            "original/MKT1.TTCS_03_0002.wav",
            "stargan_best_y/MKT1.TTCS_03_0002.wav",
        ],
    },
    {
        "question_id": "11",
        "paths": [
            "original/FKT1.TTCS_03_0004.wav",
            "stargan_best_y/FKT1.TTCS_03_0004.wav",
            "stargan_best_x/FKT1.TTCS_03_0004.wav",
        ],
    },
    {
        "question_id": "12",
        "paths": [
            "stargan_best_y/MGL1.KTXH_05_0006.wav",
            "original/MGL1.KTXH_05_0006.wav",
            "stargan_best_x/MGL1.KTXH_05_0006.wav",
        ],
    },
    {
        "question_id": "13",
        "paths": [
            "stargan_best_y/FGL1.TTCS_01_0005.wav",
            "original/FGL1.TTCS_01_0005.wav",
            "stargan_best_x/FGL1.TTCS_01_0005.wav",
        ],
    },
    {
        "question_id": "14",
        "paths": [
            "stargan_best_y/MGL1.KTXH_02_0021.wav",
            "stargan_best_x/MGL1.KTXH_02_0021.wav",
            "original/MGL1.KTXH_02_0021.wav",
        ],
    },
    {
        "question_id": "15",
        "paths": [
            "original/MGL1.TTCS_01_0005.wav",
            "stargan_best_x/MGL1.TTCS_01_0005.wav",
            "stargan_best_y/MGL1.TTCS_01_0005.wav",
        ],
    },
    {
        "question_id": "16",
        "paths": [
            "stargan_best_y/FKT1.TTCS_03_0002.wav",
            "original/FKT1.TTCS_03_0002.wav",
            "stargan_best_x/FKT1.TTCS_03_0002.wav",
        ],
    },
    {
        "question_id": "17",
        "paths": [
            "stargan_best_y/FBD1.KTXH_08_0006.wav",
            "original/FBD1.KTXH_08_0006.wav",
            "stargan_best_x/FBD1.KTXH_08_0006.wav",
        ],
    },
    {
        "question_id": "18",
        "paths": [
            "stargan_best_y/FGL1.KTXH_02_0021.wav",
            "original/FGL1.KTXH_02_0021.wav",
            "stargan_best_x/FGL1.KTXH_02_0021.wav",
        ],
    },
    {
        "question_id": "19",
        "paths": [
            "stargan_best_x/FKT1.TTCS_03_0003.wav",
            "original/FKT1.TTCS_03_0003.wav",
            "stargan_best_y/FKT1.TTCS_03_0003.wav",
        ],
    },
    {
        "question_id": "20",
        "paths": [
            "original/FBD1.KTXH_09_0023.wav",
            "stargan_best_x/FBD1.KTXH_09_0023.wav",
            "stargan_best_y/FBD1.KTXH_09_0023.wav",
        ],
    },
]


# Function to insert data into the PostgreSQL database
def insert_scoring_data(conn, question_id, filename, score, user_id):
    sql = "INSERT INTO audio_scoring (question_id, filename, score, user_id) VALUES (%s, %s, %s, %s);"
    cur = conn.cursor()
    cur.execute(sql, (question_id, filename, score, user_id))
    conn.commit()


def main():
    st.title("Audio Scoring App")

    # Adding the guideline text
    st.write("In each question, there will be 3 audio files:")
    st.write("1. Two audio files from our models.")
    st.write("2. One audio file which is the true recording.")
    st.write("Please listen to all of them and then select the score.")
    st.write("-1 means unrealistic, 100 means perfect")

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

    # Connect to the PostgreSQL database using environment variables
    conn = psycopg2.connect(
        host=os.environ.get("DATABASE_HOST"),
        port=os.environ.get("DATABASE_PORT"),
        database=os.environ.get("DATABASE_NAME"),
        user=os.environ.get("DATABASE_USER"),
        password=os.environ.get("DATABASE_PASSWORD"),
    )

    for audio_info in audio_data:
        question_id = audio_info["question_id"]
        st.write(f"Question {question_id}")
        st.write("Scorings:")

        block_paths = audio_info["paths"]
        block_scores = []

        for i, path in enumerate(block_paths):
            audio_bytes = BytesIO(
                open(os.path.join("audios", path), "rb").read()
            )
            st.audio(audio_bytes, format="audio/wav")

            score = st.slider(
                f"Score for audio file {i+1}:",
                min_value=-1,
                max_value=100,
                value=50,
                key=path,
            )

            block_scores.append(score)

            # Persist data to PostgreSQL database
            insert_scoring_data(
                conn, question_id, path, score, st.session_state.user_id
            )

        if None not in block_scores:
            # You can use the block_scores list as needed
            pass

        st.write("---")

    conn.close()


if __name__ == "__main__":
    main()
