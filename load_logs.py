import re
from datetime import datetime
import psycopg2
from config import DB_CONFIG

def parse_log_line(line):
    # Парсим строку лога с помощью регулярного выражения
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| query: (.*?) \| response: (.*?) \| satisfaction: (\d)(.*)'
    match = re.match(pattern, line)
    
    if match:
        timestamp, query, response, satisfaction, error_info = match.groups()
        error_category = error_info.strip(' |') if error_info else None
        return {
            'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
            'query': query,
            'response': response,
            'satisfaction': int(satisfaction),
            'error_category': error_category
        }
    return None

def load_logs_to_db():
    # Подключаемся к базе данных
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Очищаем таблицу
    cur.execute('TRUNCATE TABLE chatbot_logs')
    
    # Читаем лог-файл
    with open('chatbot.log', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('//'):  # Пропускаем пустые строки и комментарии
                data = parse_log_line(line)
                if data:
                    cur.execute('''
                        INSERT INTO chatbot_logs 
                        (timestamp, query, response, satisfaction, error_category)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (
                        data['timestamp'],
                        data['query'],
                        data['response'],
                        data['satisfaction'],
                        data['error_category']
                    ))
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    load_logs_to_db()
