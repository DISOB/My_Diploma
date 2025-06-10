import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.utils import COLORS
import pandas as pd

def show_developer_view(df):
    """Отображение детального анализа категорий"""
    # Кнопка возврата на главную
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← На главную"):
            st.session_state.page = 'main'
            st.rerun()
            
    with col_title:
       # st.title("Анализ категорий")
    
     tab1, tab2, tab3 = st.tabs(["📊 Анализ категорий", "📈 Временной анализ", "📝 Детальные данные"])
    
    with tab1:
        show_category_analysis(df)
    
    with tab2:
        show_time_analysis(df)
    
    with tab3:
        show_detailed_data(df)

def show_category_analysis(df):
    """Анализ категорий и подкатегорий"""
    # График по основным категориям
    category_stats = df.groupby('category', as_index=False).agg({
        'satisfaction': ['count', lambda x: (x == 1).mean() * 100]
    })
    category_stats.columns = ['category', 'count', 'success_rate']
    
    fig_categories = px.bar(
        category_stats,
        x='category',
        y='count',
        color='success_rate',
        title='Детальный анализ категорий',
        labels={
            'category': 'Категория',
            'count': 'Количество запросов',
            'success_rate': 'Успешность (%)'
        },
        color_continuous_scale=['red', 'yellow', 'green']
    )
    st.plotly_chart(fig_categories, use_container_width=True)
    
    # Анализ подкатегорий учебных запросов
    study_df = df[df['category'] == 'Учеба']
    if not study_df.empty:
        # Добавляем якорь для прокрутки
        st.markdown("<div id='subcategories'></div>", unsafe_allow_html=True)
        
        subcategory_stats = study_df.groupby('subcategory', as_index=False).agg({
            'satisfaction': ['count', lambda x: (x == 1).mean() * 100]
        })
        subcategory_stats.columns = ['subcategory', 'count', 'success_rate']
        
       
        
        fig_subcategories = px.bar(
            subcategory_stats,
            x='subcategory',
            y='count',
            color='success_rate',
            title='Детальный анализ подкатегорий учебных запросов',
            labels={
                'subcategory': 'Подкатегория',
                'count': 'Количество запросов',
                'success_rate': 'Успешность (%)'
            },
            color_continuous_scale=['red', 'yellow', 'green']
        )
        fig_subcategories.update_layout(
            xaxis_tickangle=-45,
            height=600
        )
        st.plotly_chart(fig_subcategories, use_container_width=True)

def show_time_analysis(df):
    """Временной анализ"""
    # График активности по часам с успешностью
    df['hour'] = df['timestamp'].dt.hour
    hourly_stats = df.groupby('hour', as_index=False).agg({
        'satisfaction': ['count', lambda x: (x == 1).mean() * 100]
    })
    hourly_stats.columns = ['hour', 'total_requests', 'success_rate']
    
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Bar(
        x=hourly_stats['hour'],
        y=hourly_stats['total_requests'],
        name='Количество запросов',
        marker_color='lightblue'
    ))
    fig_hourly.add_trace(go.Scatter(
        x=hourly_stats['hour'],
        y=hourly_stats['success_rate'],
        name='Успешность (%)',
        yaxis='y2',
        line=dict(color='green', width=2)
    ))
    
    fig_hourly.update_layout(
        title='Распределение запросов и успешности по часам',
        xaxis_title='Час',
        yaxis_title='Количество запросов',
        yaxis2=dict(
            title='Успешность (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        hovermode='x unified'
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Тепловая карта активности
    df['date'] = df['timestamp'].dt.date
    daily_hourly = df.groupby(['date', 'hour']).size().reset_index(name='count')
    fig_heatmap = px.density_heatmap(
        daily_hourly,
        x='hour',
        y='date',
        z='count',
        title='Тепловая карта активности',
        labels={'hour': 'Час', 'date': 'Дата', 'count': 'Количество запросов'}
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

def show_detailed_data(df):
    """Отображение детальных данных"""
    st.write("### 📋 Детальные данные")
    
    # Фильтры для детальных данных
    satisfaction_filter = st.selectbox(
        "Фильтр по успешности",
        ['Все', 'Удовлетворительно', 'Неудовлетворительно']
    )
    
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
    
    # Применяем фильтр
    if satisfaction_filter == 'Удовлетворительно':
        filtered_df = df[df['satisfaction'] == 1]
    elif satisfaction_filter == 'Неудовлетворительно':
        filtered_df = df[df['satisfaction'] == 0]
    else:
        filtered_df = df
    
    # Подготавливаем данные
    display_df = (filtered_df[columns_to_show.keys()]
                 .sort_values(['date', 'question_time'], ascending=[False, False])
                 .rename(columns=columns_to_show)
                 .copy())
    
    # Меняем значения в столбце статуса
    display_df['Статус'] = display_df['Статус'].map({
        1: 'Удовлетворительно',
        0: 'Неудовлетворительно'
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
        "chat_analysis.csv",
        "text/csv",
        key='download-csv'
    )

