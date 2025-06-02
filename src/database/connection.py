from config import DB_CONFIG
import psycopg2
import pandas as pd
import streamlit as st

def load_data_from_db():
    """Загрузка данных из базы данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = """
            SELECT timestamp, query, response, satisfaction, 
                   CASE WHEN satisfaction = 1 THEN 'success' ELSE error_category END as error_category
            FROM chatbot_logs
            ORDER BY timestamp
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Convert timestamp to datetime if it's not already
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке данных из базы: {str(e)}")
        return pd.DataFrame()
