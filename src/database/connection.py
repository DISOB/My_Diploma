from config import DB_CONFIG
import pandas as pd
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine

def load_data_from_db():
    """Загрузка данных из базы данных"""
    try:
        # Создаем URL подключения для SQLAlchemy
        db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        
        # Создаем движок SQLAlchemy
        engine = create_engine(db_url)
        
        # Выполняем запрос через SQLAlchemy
        query = """
            SELECT 
                date,
                question_time,
                answer_time,
                name,
                campus,
                education_level,
                category,
                subcategory,
                query,
                response,
                satisfaction,
                date || ' ' || question_time as timestamp
            FROM chatbot_logs
            ORDER BY date, question_time
        """
        
        # Читаем данные с помощью pandas
        df = pd.read_sql(query, engine)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Преобразуем колонки в нужный формат
        df['question_time'] = pd.to_datetime(df['question_time'], format='%H:%M:%S').dt.time
        df['answer_time'] = pd.to_datetime(df['answer_time'], format='%H:%M:%S').dt.time
        
        # Добавляем категорию ошибки на основе satisfaction
        df['error_category'] = df['satisfaction'].map(
            lambda x: 'success' if x == 1 else 'incorrect_answer'
        )
        
        # Заменяем None на NaN для корректной работы с pandas
        df = df.fillna({
            'subcategory': 'Не указано',
            'category': 'Другое',
            'campus': 'Не указан',
            'education_level': 'Не указан'
        })
        
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных из базы: {str(e)}")
        return pd.DataFrame()
