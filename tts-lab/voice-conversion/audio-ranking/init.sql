CREATE TABLE audio_scoring (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL,
    filename VARCHAR NOT NULL,
    score INTEGER NOT NULL,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
