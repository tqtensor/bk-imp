CREATE TABLE audio_ranking (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL,
    url VARCHAR NOT NULL,
    ranking INTEGER NOT NULL,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
