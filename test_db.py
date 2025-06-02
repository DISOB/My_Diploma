import psycopg2
from config import DB_CONFIG

def test_database():
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Проверяем количество записей
        cursor.execute("SELECT COUNT(*) FROM chatbot_logs")
        count = cursor.fetchone()[0]
        print(f"Всего записей в базе данных: {count}")
        
        # Выводим несколько последних записей
        cursor.execute("""            SELECT timestamp, query, response, satisfaction, error_category 
            FROM chatbot_logs
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        print("\nПоследние записи:")
        for row in rows:
            timestamp, query, satisfaction, error_category = row
            status = "Успешно" if satisfaction else "Ошибка"
            error_info = f" ({error_category})" if error_category and not satisfaction else ""
            print(f"{timestamp}: {query} - {status}{error_info}")
        
    except Exception as e:
        print(f"Ошибка при тестировании базы данных: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    test_database()
from config import DB_CONFIG

def test_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("Successfully connected to the database!")
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to connect to the database: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
