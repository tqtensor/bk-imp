import os
from io import BytesIO

import psycopg2
import requests
import streamlit as st


# Function to insert data into the PostgreSQL database
def insert_ranking_data(conn, question_num, url, ranking):
    sql = "INSERT INTO audio_rankings (question_num, url, ranking) VALUES (%s, %s, %s);"
    cur = conn.cursor()
    cur.execute(sql, (question_num, url, ranking))
    conn.commit()


def main():
    audio_data = [
        {
            "name": "Audio",
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
        },
    ]

    rankings = {}

    audio = audio_data[0]
    urls = audio["urls"]
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
            insert_ranking_data(conn, question_num, url, ranking)

        if None not in block_rankings:
            rankings[f"Question {question_num}"] = block_rankings

        st.write("---")

    conn.close()

    st.write("Overall Rankings:")
    for question_name, question_rankings in rankings.items():
        st.write(f"{question_name}: {question_rankings}")


if __name__ == "__main__":
    main()
