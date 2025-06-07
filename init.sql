\c chatbot_metrics;

DROP TABLE IF EXISTS chatbot_logs;

CREATE TABLE chatbot_logs (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    question_time TIME NOT NULL,
    answer_time TIME NOT NULL,
    name VARCHAR(100) NOT NULL,
    campus VARCHAR(50) NOT NULL,
    education_level VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    satisfaction INTEGER CHECK (satisfaction IN (0, 1))
);
