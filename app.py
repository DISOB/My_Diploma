import streamlit as st
from src.database import load_data_from_db
from src.utils import parse_log_file, load_data_from_file
from src.views import show_metrics, show_standard_view, show_developer_view

# Настройка страницы
st.set_page_config(
    page_title="Log File Dashboard",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Анализ лог файла")
    
    # Переключатель режимов
    is_developer = st.sidebar.checkbox("Режим разработчика", False)
    
    # Загружаем данные из базы
    df = load_data_from_db()
    
    if df.empty:
        st.error("Не удалось загрузить данные из базы данных")
        st.stop()
    
    # Фильтры
    st.sidebar.subheader("Фильтры")
    
    # Фильтр по датам
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    
    # Создаем два поля для выбора начальной и конечной даты
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(
            "С",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
    with col2:
        end_date = st.date_input(
            "По",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    
    # Применяем фильтр по дате
    mask = (
        (df['timestamp'].dt.date >= start_date) & 
        (df['timestamp'].dt.date <= end_date)
    )
    df = df[mask]
    
    # Основные метрики
    st.subheader("Основные метрики")
    show_metrics(df)
    
    if is_developer:
        st.divider()
        st.subheader("🔧 Расширенная аналитика (режим разработчика)")
        show_developer_view(df)
    else:
        st.subheader("Общая статистика")
        show_standard_view(df)

if __name__ == "__main__":
    main()