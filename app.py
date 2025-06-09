import streamlit as st
from src.database import load_data_from_db
from src.utils import parse_log_file, load_data_from_file
from src.views import show_metrics, show_standard_view, show_developer_view
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Метрики чат-бота",
    page_icon="📊",
    layout="wide"
)

def apply_filters(df):
    """Применение фильтров к данным"""
    st.write("### Фильтры")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Фильтр по датам
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        start_date = st.date_input(
            "Период с",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
        end_date = st.date_input(
            "По",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        # Фильтр по категориям
        categories = ['Все'] + list(df['category'].unique())
        selected_category = st.selectbox('Категория', categories)
        
        if selected_category == 'Учеба':
            subcategories = ['Все'] + [
                'Учебный процесс', 'Практическая подготовка', 'ГИА', 
                'Траектория обучения', 'Английский язык', 
                'Цифровые компетенции', 'Перемещения / Изменение статуса студента',
                'онлайн-обучение', 'Дополнительное образование', 'ОВЗ', 'Выпускникам'
            ]
            selected_subcategory = st.selectbox('Подкатегория', subcategories)
        else:
            selected_subcategory = 'Все'
    
    with col3:
        # Фильтр по кампусам
        campuses = ['Все'] + list(df['campus'].unique())
        selected_campus = st.selectbox('Кампус', campuses)
        
        # Фильтр по уровню образования
        education_levels = ['Все'] + list(df['education_level'].unique())
        selected_education = st.selectbox('Уровень образования', education_levels)
    
    # Применяем фильтры
    mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
    if selected_category != 'Все':
        mask &= df['category'] == selected_category
    if selected_subcategory != 'Все' and selected_category == 'Учеба':
        mask &= df['subcategory'] == selected_subcategory
    if selected_campus != 'Все':
        mask &= df['campus'] == selected_campus
    if selected_education != 'Все':
        mask &= df['education_level'] == selected_education
    
    return df[mask]

def main():
    # Загрузка данных
    df = load_data_from_db()
    if df.empty:
        st.error("Не удалось загрузить данные из базы данных")
        st.stop()
    
    # Инициализация состояния страницы
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    
    # Навигационное меню
    pages = {
        'main': '📊 Главная',
        'success_rate': '📈 Успешность ответов',
        'categories': '🎓 Статистика по категориям',
        'response_time': '⏱️ Время ответа'
    }
    
    selected_page = st.selectbox(
        'Навигация',
        list(pages.keys()),
        format_func=lambda x: pages[x],
        index=list(pages.keys()).index(st.session_state.page)
    )
    st.session_state.page = selected_page
    
    # Фильтруем данные
    filtered_df = apply_filters(df)
    
    # Отображаем контент в зависимости от выбранной страницы
    if st.session_state.page == 'main':
        st.title("📊 Основные метрики")
        show_metrics(filtered_df)
    elif st.session_state.page == 'success_rate':
        st.title("📈 Анализ успешности ответов")
        show_standard_view(filtered_df)
    elif st.session_state.page == 'categories':
        st.title("🎓 Анализ категорий")
        show_developer_view(filtered_df)
    elif st.session_state.page == 'response_time':
        st.title("⏱️ Анализ времени ответа")
        show_standard_view(filtered_df, section='response_time')

if __name__ == "__main__":
    main()