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
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        .metric-container:hover {
            transform: translateY(-2px);
            box-shadow: rgba(0, 0, 0, 0.15) 0px 8px 24px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: 600;
            color: #1f1f1f;
            margin: 8px 0;
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
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
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-top: 24px;
        }
        .stats-grid {
            display: grid;
            gap: 24px;
            margin-bottom: 24px;
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
        success_rate = (df['satisfaction'] == 1).mean() * 100
        avg_response_time = df['response_time'].mean()
        satisfied_count = len(df[df['satisfaction'] == 1])
        unsatisfied_count = len(df[df['satisfaction'] == 0])
        satisfaction_rate = satisfied_count / (satisfied_count + unsatisfied_count) if satisfied_count + unsatisfied_count > 0 else 0
        
        # Тренды и статусы
        success_status = "positive" if success_rate >= 90 else "warning" if success_rate >= 75 else "negative"
        response_status = "positive" if avg_response_time <= 2 else "warning" if avg_response_time <= 3 else "negative"
        satisfaction_status = "positive" if satisfaction_rate >= 0.9 else "warning" if satisfaction_rate >= 0.75 else "negative"
    else:
        success_rate = avg_response_time = satisfied_count = unsatisfied_count = satisfaction_rate = 0
        success_status = response_status = satisfaction_status = "negative"

    # Основной контейнер с метриками
    metrics_col, alerts_col = st.columns([3, 1])

    with metrics_col:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                <div class='metric-container'>
                    <div class='metric-label'>Общая успешность</div>
                    <div class='metric-value'>{success_rate:.1f}%</div>
                    <div class='metric-subtitle'>всего {len(df):,} запросов</div>
                    <div class='trend-indicator {success_status}-trend'>
                        {"✨ Отличная работа" if success_status == "positive" else "⚠️ Требует внимания" if success_status == "warning" else "❌ Критический уровень"}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📊 Подробная статистика", type="primary", use_container_width=True):
                st.session_state.page = 'categories'

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
            if st.button("⏱️ Анализ времени", type="primary", use_container_width=True):
                st.session_state.page = 'response_time'

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
            if st.button("📈 Анализ удовлетворенности", type="primary", use_container_width=True):
                st.session_state.page = 'success_rate'

    # Правая колонка с предупреждениями
    with alerts_col:
        st.markdown("""
            <div class='alerts-container'>
                <h3 style='margin-bottom: 16px; font-size: 18px; font-weight: 600; color: #0f172a;'>
                    🎯 Статус системы
                </h3>
        """, unsafe_allow_html=True)
        
        if len(df) > 0:
            warnings = []
            if success_rate < 90:
                severity = "критически " if success_rate < 75 else ""
                warnings.append(f"❗ {severity}Низкая успешность ответов ({success_rate:.1f}%)")
            if avg_response_time > 2:
                severity = "очень " if avg_response_time > 3 else ""
                warnings.append(f"⚡ {severity}Высокое время ответа ({avg_response_time:.1f}с)")
            if satisfaction_rate < 0.9:
                severity = "критически " if satisfaction_rate < 0.75 else ""
                warnings.append(f"😕 {severity}Низкая удовлетворенность ({satisfaction_rate*100:.1f}%)")

            if warnings:
                for warning in warnings:
                    st.markdown(f"<div class='alert-card'>{warning}</div>", unsafe_allow_html=True)
                
                st.markdown("""
                    <div style='margin-top: 16px; font-size: 14px; color: #64748b;'>
                        Рекомендуется обратить внимание на отмеченные показатели
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='success-card'>
                        ✅ Все показатели в норме
                    </div>
                    <div style='margin-top: 16px; font-size: 14px; color: #64748b;'>
                        Система работает эффективно
                    </div>
                """, unsafe_allow_html=True)
        
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
        
        cat_col1, cat_col2 = st.columns([2, 1])
        
        with cat_col1:
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

            if st.button("🔍 Детальный анализ категорий", use_container_width=True):
                st.session_state.page = 'categories'

        with cat_col2:
            if df['category'].eq('Учеба').any():
                study_df = df[df['category'] == 'Учеба']
                study_stats = study_df['subcategory'].value_counts()
                top_subcategory = study_stats.index[0] if not study_stats.empty else "Нет данных"
                subcategory_count = study_stats.iloc[0] if not study_stats.empty else 0
                subcategory_percentage = (subcategory_count / len(study_df) * 100) if len(study_df) > 0 else 0
                
                st.markdown(f"""
                    <div class='metric-container' style='margin-bottom: 0;'>
                        <div class='metric-label'>Топ подкатегория учебы</div>
                        <div class='metric-value' style='font-size: 24px;'>{top_subcategory}</div>
                        <div class='metric-subtitle' style='display: flex; justify-content: space-between;'>
                            <span>{subcategory_count:,} запросов</span>
                            <span style='color: #0284c7;'>{subcategory_percentage:.1f}%</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
