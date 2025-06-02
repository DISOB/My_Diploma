\c chatbot_metrics;

DROP TABLE IF EXISTS chatbot_logs;

CREATE TABLE chatbot_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    satisfaction INTEGER CHECK (satisfaction IN (0, 1)),
    error_category TEXT
);
