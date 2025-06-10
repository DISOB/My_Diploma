import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.views.standard import calculate_response_time

def show_metrics(df):
    """Отображение основных метрик"""
    # Добавляем CSS для современного дизайна
    st.markdown("""
        <style>
        .dashboard {
            padding: 1rem;
        }
        .metric-container {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
            margin-bottom: 24px;
            position: relative;
            height: 280px; /* Фиксированная высота для всех контейнеров */
            display: flex;
            flex-direction: column;
            transition: transform 0.2s ease, box-shadow 0.2s ease;  /* Добавляем плавный переход */
        }
        
        .metric-container:hover {
            transform: translateY(-5px);  /* Эффект поднятия при наведении */
            box-shadow: rgba(0, 0, 0, 0.15) 0px 8px 24px;  /* Усиление тени при наведении */
        }
        .metric-value {
            font-size: 32px;
            font-weight: 600;
            color: #1f1f1f;
            margin: 8px 0;
            flex-grow: 0;
        }
        .metric-label {
            color: #666;
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .metric-subtitle {
            font-size: 14px;
            color: #666;
            margin-top: 4px;
        }
        .trend-indicator {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 500;
            margin-top: 12px;
        }
        .positive-trend {
            background-color: #ecfdf3;
            color: #027948;
        }
        .warning-trend {
            background-color: #fff7ed;
            color: #9a3412;
        }
        .negative-trend {
            background-color: #fef2f2;
            color: #dc2626;
        }
        .alerts-container {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
        }
        .alert-card {
            background-color: #fff7ed;
            border-left: 4px solid #fb923c;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            font-size: 14px;
        }
        .success-card {
            background-color: #ecfdf5;
            border-left: 4px solid #34d399;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            font-size: 14px;
        }
        .category-info {
            /* Removing background and border */
            background-color: transparent;
            border: none;
            border-radius: 12px;
            padding: 20px;
            margin-top: 24px;
        }
        .stats-grid {
            display: grid;
            gap: 24px;
            margin-bottom: 24px;
        }
        
        /* Стили для кнопок внутри контейнеров */
        .metric-button {
            position: absolute;
            bottom: 24px;
            left: 24px;
            right: 24px;
            margin-top: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='dashboard'>
            <h1 style='text-align: center; margin-bottom: 32px; font-size: 2.5rem; font-weight: 600; color: #0f172a;'>
                📊 Ключевые показатели
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # Вычисляем метрики
    if len(df) > 0:
        df = calculate_response_time(df)
        error_count = len(df[df['satisfaction'] == 0])
        total_count = len(df)
        error_rate = (error_count / total_count) * 100
        avg_response_time = df['response_time'].mean()
        satisfied_count = len(df[df['satisfaction'] == 1])
        unsatisfied_count = len(df[df['satisfaction'] == 0])
        satisfaction_rate = satisfied_count / total_count if total_count > 0 else 0
        
        # Тренды и статусы (инвертируем логику для ошибок)
        error_status = "positive" if error_rate <= 10 else "warning" if error_rate <= 25 else "negative"
        response_status = "positive" if avg_response_time <= 2 else "warning" if avg_response_time <= 3 else "negative"
        satisfaction_status = "positive" if satisfaction_rate >= 0.9 else "warning" if satisfaction_rate >= 0.75 else "negative"
    else:
        error_count = total_count = avg_response_time = satisfied_count = unsatisfied_count = satisfaction_rate = 0
        error_status = response_status = satisfaction_status = "negative"

    # Основной контейнер с метриками
    st.write("")  # Добавляем отступ
    col1, col2, col3 = st.columns([1, 1, 1])  # Равные колонки

    with col1:
        st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-label'>Ошибочные выходы</div>
                <div class='metric-value' style='font-size: 28px;'>{error_count}</div>
                <div class='metric-subtitle' style='display: flex; justify-content: space-between;'>
                    <span>{error_rate:.1f}% от общего числа</span>
                </div>
                <div class='trend-indicator {error_status}-trend'>
                    {"✨ Низкий уровень ошибок" if error_status == "positive" 
                     else "⚠️ Требует внимания" if error_status == "warning" 
                     else "❌ Высокий уровень ошибок"}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='metric-button'>", unsafe_allow_html=True)
        if st.button("❌ Анализ ошибочных выходов", type="primary", use_container_width=True):
            st.session_state.page = 'errors'
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-label'>Среднее время ответа</div>
                <div class='metric-value'>{avg_response_time:.1f}с</div>
                <div class='metric-subtitle'>секунд в среднем</div>
                <div class='trend-indicator {response_status}-trend'>
                    {"⚡ Быстрый отклик" if response_status == "positive" else "⏳ Средняя скорость" if response_status == "warning" else "🐌 Медленный отклик"}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='metric-button'>", unsafe_allow_html=True)
        if st.button("⏱️ Анализ времени", type="primary", use_container_width=True):
            st.session_state.page = 'response_time'
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class='metric-container'>
                <div class='metric-label'>Удовлетворенность</div>
                <div class='metric-value'>{satisfaction_rate * 100:.1f}%</div>
                <div class='metric-subtitle'>👍 {satisfied_count} / 👎 {unsatisfied_count}</div>
                <div class='trend-indicator {satisfaction_status}-trend'>
                    {"🌟 Высокая" if satisfaction_status == "positive" else "😐 Средняя" if satisfaction_status == "warning" else "😟 Низкая"}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='metric-button'>", unsafe_allow_html=True)
        if st.button("📈 Анализ удовлетворенности", type="primary", use_container_width=True):
            st.session_state.page = 'success_rate'
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Дополнительная информация о категориях
    st.markdown(f"""
        <div class='category-info'>
            <h3 style='margin-bottom: 24px; font-size: 1.5rem; font-weight: 600; color: #0f172a;'>
                📈 Распределение по категориям
            </h3>
        </div>
    """, unsafe_allow_html=True)

    if len(df) > 0:
        categories = df['category'].value_counts()
        main_category = categories.index[0] if not categories.empty else "Нет данных"
        category_count = categories.iloc[0] if not categories.empty else 0
        total_requests = len(df)
        category_percentage = (category_count / total_requests * 100) if total_requests > 0 else 0
        
        st.markdown(f"""
            <div class='metric-container' style='margin-bottom: 0;'>
                <div class='metric-label'>Самая популярная категория</div>
                <div class='metric-value' style='font-size: 28px;'>{main_category}</div>
                <div class='metric-subtitle' style='display: flex; justify-content: space-between;'>
                    <span>{category_count:,} запросов</span>
                    <span style='color: #0284c7;'>{category_percentage:.1f}% от общего числа</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        if st.button("🔍 Детальный анализ категорий", type="primary", use_container_width=True):
            st.session_state.page = 'categories'
        st.markdown("</div>", unsafe_allow_html=True)
