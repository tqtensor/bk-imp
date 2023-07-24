CREATE TABLE audio_rankings (
    id SERIAL PRIMARY KEY,
    question_num INTEGER NOT NULL,
    url VARCHAR NOT NULL,
    ranking INTEGER NOT NULL
);
