import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.utils import COLORS

def show_error_analysis(df):
    """Отображение анализа ошибочных запросов"""
    # Фильтруем только ошибочные запросы сразу в начале
    error_df = df[df['satisfaction'] == 0]
    
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← На главную"):
            st.session_state.page = 'main'
            st.rerun()
    
    with col_title:
        st.title("❌ Анализ ошибочных выходов")
    
    # Показываем общую статистику
    total_errors = len(error_df)
    total_requests = len(df)
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
    
    st.markdown(f"""
        ### 📊 Общая статистика выходов
        - Всего ошибочных выходов: **{total_errors:,}**
        - Процент ошибочных выходов: **{error_rate:.1f}%**
        - Всего запросов: **{total_requests:,}**
    """)
    
    tab1, tab2, tab3 = st.tabs([
        "📊 выходы по категориям", 
        "📈 Типы выходов",
        "📝 Детальные данные"
    ])
    
    with tab1:
        # Анализ ошибок по категориям
        category_errors = error_df.groupby('category').agg({
            'satisfaction': 'count',
        }).reset_index()
        category_errors.columns = ['category', 'error_count']
        category_errors['error_rate'] = category_errors['error_count'] / category_errors['error_count'].sum() * 100
        
        fig_category_errors = px.bar(
            category_errors.sort_values('error_count', ascending=True),
            y='category',
            x='error_count',
            orientation='h',
            title='Распределение ошибочных выходов по категориям',
            labels={
                'category': 'Категория',
                'error_count': 'Количество ошибочных выходов',
            },
            text=category_errors['error_rate'].round(1).astype(str) + '%'
        )
        fig_category_errors.update_traces(
            textposition='auto',
            marker_color=COLORS['incorrect_answer']
        )
        st.plotly_chart(fig_category_errors, use_container_width=True)
        
        # Если есть подкатегории в учебных запросах
        study_errors = error_df[error_df['category'] == 'Учеба']
        if not study_errors.empty:
            subcategory_errors = study_errors.groupby('subcategory').agg({
                'satisfaction': 'count'
            }).reset_index()
            subcategory_errors.columns = ['subcategory', 'error_count']
            subcategory_errors['error_rate'] = subcategory_errors['error_count'] / subcategory_errors['error_count'].sum() * 100
            
            fig_subcategory_errors = px.bar(
                subcategory_errors.sort_values('error_count', ascending=True),
                y='subcategory',
                x='error_count',
                orientation='h',
                title='Распределение ошибочных выходов по подкатегориям учебных запросов',
                labels={
                    'subcategory': 'Подкатегория',
                    'error_count': 'Количество выходов'
                },
                text=subcategory_errors['error_rate'].round(1).astype(str) + '%'
            )
            fig_subcategory_errors.update_traces(
                textposition='auto',
                marker_color=COLORS['incorrect_answer']
            )
            st.plotly_chart(fig_subcategory_errors, use_container_width=True)
    
    with tab2:
        
        
        # Анализируем ответы на наличие ключевых фраз
        def categorize_error(response):
            response = response.lower()
            if 'система не отвечает' in response:
                return 'Система не отвечает'
            elif 'не относится к вшэ' in response:
                return 'Вопрос не относится к ВШЭ'
            elif 'неуместно' in response:
                return 'Неуместный вопрос'
            else:
                return 'Другие ошибки'
        
        error_df['error_type'] = error_df['response'].apply(categorize_error)
        error_types = error_df.groupby('error_type').size().reset_index(name='count')
        error_types['percentage'] = (error_types['count'] / len(error_df) * 100).round(1)
        
        # Сортируем типы ошибок в нужном порядке
        error_type_order = [
            'Вопрос не относится к ВШЭ',
            'Неуместный вопрос',
            'Система не отвечает',
            'Другие ошибки'
        ]
        error_types['error_type'] = pd.Categorical(
            error_types['error_type'], 
            categories=error_type_order, 
            ordered=True
        )
        error_types = error_types.sort_values('error_type')
        
        fig_error_types = px.pie(
            error_types,
            values='count',
            names='error_type',
            title='Распределние по типам ошибочных выходов',
            color_discrete_sequence=[
                '#FF6B6B',  # Красный для вопросов не по теме
                '#FFB366',  # Оранжевый для неуместных вопросов
                '#FF99CC',  # Розовый для системных ошибок
                '#B8B8B8'   # Серый для других ошибок
            ],
            hover_data=['percentage']
        )
        
        fig_error_types.update_traces(
            textinfo='percent',
            textposition='inside'
        )
        
        # Увеличиваем размер диаграммы
        fig_error_types.update_layout(
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_error_types, use_container_width=True)
        
        # Таблица с детализацией типов ошибок
        st.write("### Детализация типов ошибочных выходов")
        error_details = pd.DataFrame({
            'Тип ошибки': error_types['error_type'],
            'Количество': error_types['count'],
            'Процент': error_types['percentage'].map('{:.1f}%'.format)
        })
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.dataframe(error_details, hide_index=True)
        with col2:
            st.download_button(
                "📥 Скачать данные (CSV)",
                error_details.to_csv(index=False).encode('utf-8-sig'),
                "error_types_analysis.csv",
                "text/csv",
                key='download-csv-errors'
            )
    
    with tab3:
        
        
        # Определяем колонки и их русские названия
        columns_to_show = {
            'date': 'Дата',
            'question_time': 'Время вопроса',
            'answer_time': 'Время ответа',
            'name': 'Имя',
            'campus': 'Кампус',
            'education_level': 'Уровень образования',
            'category': 'Категория',
            'subcategory': 'Подкатегория',
            'query': 'Запрос',
            'response': 'Ответ',
            'satisfaction': 'Статус'
        }
        
        # Фильтруем только ошибочные запросы
        error_df = df[df['satisfaction'] == 0]
        
        # Подготавливаем данные
        display_df = (error_df[columns_to_show.keys()]
                     .sort_values(['date', 'question_time'], ascending=[False, False])
                     .rename(columns=columns_to_show)
                     .copy())
        
        # Меняем значения в столбце статуса
        display_df['Статус'] = display_df['Статус'].map({
            1: '✅ Удовлетворительно',
            0: '❌ Неудовлетворительно'
        })
        
        # Отображаем таблицу
        st.dataframe(
            display_df.reset_index(drop=True),
            hide_index=True
        )
        
        # Экспорт данных
        st.download_button(
            "📥 Скачать данные (CSV)",
            display_df.to_csv(index=False).encode('utf-8-sig'),
            "error_analysis.csv",
            "text/csv",
            key='download-csv'
        )