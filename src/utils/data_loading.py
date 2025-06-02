import pandas as pd
from datetime import datetime
import streamlit as st

def parse_log_file(file) -> pd.DataFrame:
    """Парсинг лог файла и преобразование в DataFrame"""
    try:
        # Read all lines from the file
        content = file.getvalue().decode('utf-8').splitlines()
        
        # Parse each line into components
        data = []
        for line in content:
            parts = line.strip().split(' | ')
            if len(parts) >= 4:  # Minimum required parts
                timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                query = parts[1].split(': ')[1]
                response = parts[2].split(': ')[1]
                satisfaction = int(parts[3].split(': ')[1])
                error_category = 'success' if satisfaction == 1 else parts[4] if len(parts) > 4 else 'other_error'
                
                data.append({
                    'timestamp': timestamp,
                    'query': query,
                    'response': response,
                    'satisfaction': satisfaction,
                    'error_category': error_category
                })
        
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Ошибка при парсинге лог файла: {str(e)}")
        return pd.DataFrame()

def load_data_from_file(file):
    """Загрузка данных из файла CSV"""
    try:
        df = pd.read_csv(file)
        # Convert timestamp to datetime if it's not already
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке файла: {str(e)}")
        return pd.DataFrame()
