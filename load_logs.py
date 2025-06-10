import re
from datetime import datetime
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
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

def load_csv_to_db():
    """Загрузка данных из CSV в базу данных"""
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Очищаем таблицу
        cur.execute('TRUNCATE TABLE chatbot_logs')
        
        # Читаем CSV файл, пропуская первую строку как заголовок
        df = pd.read_csv('chatbotlog.csv', header=0)
        
        # Подготавливаем данные для вставки
        data = []
        for _, row in df.iterrows():
            try:
                # Преобразуем строки в объекты datetime и извлекаем нужные компоненты
                date = pd.to_datetime(row['Дата']).strftime('%Y-%m-%d')
                question_time = pd.to_datetime(row['Время вопроса']).strftime('%H:%M:%S')
                answer_time = pd.to_datetime(row['Время ответа']).strftime('%H:%M:%S')
                
                data.append((
                    date,
                    question_time,
                    answer_time,
                    row['Имя'],
                    row['Кампус'],
                    row['Уровень образования'],
                    row['Категория'],
                    row['Подкатегория'] if pd.notna(row['Подкатегория']) else None,
                    row['Запрос'],
                    row['Ответ'],
                    row['Доволен']
                ))
            except Exception as e:
                print(f"Ошибка при обработке строки: {row}")
                print(f"Ошибка: {str(e)}")
                continue
        
        # Вставляем данные пакетами
        execute_batch(cur, '''
            INSERT INTO chatbot_logs 
            (date, question_time, answer_time, name, campus, 
             education_level, category, subcategory, query, 
             response, satisfaction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', data)
        
        # Сохраняем изменения и закрываем соединение
        conn.commit()
        print(f"Успешно загружено {len(data)} записей")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    load_csv_to_db()
