-- data/init.sql
CREATE TABLE IF NOT EXISTS chatbot_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    dau INTEGER,
    wau INTEGER,
    mau INTEGER,
    total_sessions INTEGER,
    avg_session_duration_sec INTEGER,
    avg_messages_per_session FLOAT,
    success_rate FLOAT,
    unknown_answer_rate FLOAT,
    escalation_rate FLOAT,
    avg_response_time_ms INTEGER,
    uptime_percent FLOAT,
    unique_students_dau INTEGER,
    unique_students_wau INTEGER,
    unique_students_mau INTEGER,
    exam_period_requests INTEGER,
    top_topic_1 VARCHAR(100),
    top_topic_2 VARCHAR(100),
    top_topic_3 VARCHAR(100),
    csat_score FLOAT,
    negative_feedback_rate FLOAT,
    questions_handled INTEGER
);
CREATE INDEX IF NOT EXISTS idx_chatbot_metrics_date ON chatbot_metrics(date);