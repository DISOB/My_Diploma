import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
from config.settings import DB_CONFIG

@st.cache_data
def load_data():
    connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['dbname']}"
    engine = create_engine(connection_string)
    try:
        df = pd.read_sql("SELECT * FROM chatbot_metrics ORDER BY date DESC", engine)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Ошибка подключения к базе данных: {str(e)}")
        return None
