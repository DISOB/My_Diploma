from pathlib import Path
import pandas as pd
import psycopg2
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")

# Путь к файлу Excel
excel_file = Path("/app/data/chatbot_metrics.xlsx")

DB_CONFIG = {
    "dbname": "chatbot_db",
    "user": "myuser",
    "password": "1212",
    "host": "db"  # для Docker!
}


def import_excel_to_metrics():
    try:
        # Проверка наличия файла
        if not excel_file.exists():
            logging.error(f"❌ Файл не найден: {excel_file}")
            return

        # Чтение файла Excel
        logging.info(f"📄 Загрузка данных из {excel_file}...")
        df = pd.read_excel(excel_file)

        # Проверка обязательных колонок
        required_columns = [
            'date', 'dau', 'wau', 'mau', 'total_sessions',
            'avg_session_duration_sec', 'avg_messages_per_session',
            'success_rate', 'unknown_answer_rate', 'escalation_rate',
            'avg_response_time_ms', 'uptime_percent',
            'unique_students_dau', 'unique_students_wau', 'unique_students_mau',
            'exam_period_requests', 'top_topic_1', 'top_topic_2', 'top_topic_3',
            'csat_score', 'negative_feedback_rate', 'questions_handled'
        ]

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logging.error(f"❌ В Excel отсутствуют колонки: {', '.join(missing_cols)}")
            return

        # Подключение к БД
        logging.info("🔌 Подключение к базе данных...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Очистка таблицы перед импортом (опционально)
        cursor.execute("DELETE FROM chatbot_metrics;")
        logging.info("🧹 Старые данные удалены.")

        # Вставка данных
        inserted = 0
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO chatbot_metrics (
                    date, dau, wau, mau, total_sessions,
                    avg_session_duration_sec, avg_messages_per_session,
                    success_rate, unknown_answer_rate, escalation_rate,
                    avg_response_time_ms, uptime_percent,
                    unique_students_dau, unique_students_wau, unique_students_mau,
                    exam_period_requests, top_topic_1, top_topic_2, top_topic_3,
                    csat_score, negative_feedback_rate, questions_handled
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                tuple(row)
            )
            inserted += 1

        conn.commit()
        logging.info(f"✅ Успешно загружено {inserted} строк.")

    except Exception as e:
        logging.error(f"❌ Произошла ошибка: {e}", exc_info=True)
        conn.rollback()
    finally:
        if 'conn' in locals() and conn.closed == 0:
            cursor.close()
            conn.close()
            logging.info("🔌 Соединение с БД закрыто.")

if __name__ == "__main__":
    import_excel_to_metrics()