import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.views.standard import calculate_response_time

def show_metrics(df):
    """Отображение основных метрик с возможностью клика"""
    st.write("### 📈 Ключевые показатели")
    
    # Вычисляем время ответа сразу для всех метрик
    if len(df) > 0:
        df = calculate_response_time(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(df) > 0:
            period = f"{df['timestamp'].min().strftime('%d.%m.%Y')} - {df['timestamp'].max().strftime('%d.%m.%Y')}"
        else:
            period = "Нет данных"
        st.metric("Временной период", period)
        
        total_requests = len(df)
        success_rate = (df['satisfaction'] == 1).mean() * 100 if len(df) > 0 else 0
        
        col1_1, col1_2 = st.columns([2, 3])
        with col1_1:
            st.metric("Всего запросов", total_requests)
        with col1_2:
            if st.button("📊 К статистике →", use_container_width=True):
                st.session_state.page = 'categories'
        
        col1_3, col1_4 = st.columns([2, 3])
        with col1_3:
            st.metric("Успешность ответов", f"{success_rate:.1f}%")
        with col1_4:
            if st.button("📈 К анализу →", use_container_width=True):
                st.session_state.page = 'success_rate'
    
    with col2:
        if len(df) > 0:
            # Анализ по категориям
            categories = df['category'].value_counts()
            main_category = categories.index[0] if not categories.empty else "Нет данных"
            category_count = categories.iloc[0] if not categories.empty else 0
            
            # Анализ подкатегорий для категории "Учеба"
            study_df = df[df['category'] == 'Учеба']
            if not study_df.empty:
                subcategories = study_df['subcategory'].value_counts()
                main_subcategory = subcategories.index[0] if not subcategories.empty else "Нет данных"
                subcategory_count = subcategories.iloc[0] if not subcategories.empty else 0
            else:
                main_subcategory = "Нет данных"
                subcategory_count = 0
            
            col2_1, col2_2 = st.columns([2, 3])
            with col2_1:
                st.metric("Основная категория", f"{main_category} ({category_count})")
            with col2_2:
                if st.button("🔍 К категориям →", use_container_width=True):
                    st.session_state.page = 'categories'
            
            col2_3, col2_4 = st.columns([2, 3])
            with col2_3:
                st.metric("Основная подкатегория учебы", f"{main_subcategory} ({subcategory_count})")
            with col2_4:
                if st.button("📚 К запросам →", use_container_width=True):
                    st.session_state.page = 'categories'
        else:
            st.metric("Основная категория", "Нет данных")
            st.metric("Основная подкатегория учебы", "Нет данных")
    
    with col3:
        if len(df) > 0:
            avg_response_time = df['response_time'].mean()
            
            col3_1, col3_2 = st.columns([2, 3])
            with col3_1:
                st.metric("Среднее время ответа", f"{avg_response_time:.1f} сек")
            with col3_2:
                if st.button("⏱️ Ко времени →", use_container_width=True):
                    st.session_state.page = 'response_time'
            
            # Количество успешных/неуспешных ответов
            satisfied_count = len(df[df['satisfaction'] == 1])
            unsatisfied_count = len(df[df['satisfaction'] == 0])
            
            col3_3, col3_4 = st.columns([2, 3])
            with col3_3:
                st.metric("Удовлетворенные", f"{satisfied_count} (👍)")
                st.metric("Неудовлетворенные", f"{unsatisfied_count} (👎)")
            with col3_4:
                if st.button("📊 К оценкам →", use_container_width=True):
                    st.session_state.page = 'success_rate'
        else:
            st.metric("Среднее время ответа", "Нет данных")
            st.metric("Удовлетворенные ответы", "0")
            st.metric("Неудовлетворенные ответы", "0")
