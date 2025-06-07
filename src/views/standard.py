import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.utils import COLORS
from datetime import datetime, timedelta

def calculate_response_time(df):
    """Вычисляет время ответа для каждой строки"""
    def time_diff(row):
        q_time = row['question_time']
        a_time = row['answer_time']
        
        base_date = datetime.now().date()
        q_datetime = datetime.combine(base_date, q_time)
        a_datetime = datetime.combine(base_date, a_time)
        
        if a_datetime < q_datetime:
            a_datetime = a_datetime + timedelta(days=1)
            
        return (a_datetime - q_datetime).total_seconds()
    
    df['response_time'] = df.apply(time_diff, axis=1)
    return df

def show_standard_view(df, section='all'):
    """Отображение стандартного режима с фокусом на определенной метрике"""
    # Сначала вычисляем время ответа для всех случаев
    df = calculate_response_time(df)
    
    if section == 'response_time':
        show_response_time_analysis(df)
    else:
        show_full_analysis(df)

def show_full_analysis(df):
    """Полный анализ данных"""
    col1, col2 = st.columns(2)
    
    with col1:
        # График соотношения успешных/неуспешных ответов
        success_count = len(df[df['satisfaction'] == 1])
        errors_count = len(df[df['satisfaction'] == 0])
        fig_success = px.pie(
            names=['Успешные', 'Ошибки'],
            values=[success_count, errors_count],
            title='Соотношение успешных и неуспешных ответов',
            color_discrete_sequence=[COLORS['success'], COLORS['incorrect_answer']]
        )
        fig_success.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<br>".join([
                "%{label}",
                "Количество: %{value}",
                "Процент: %{percent}"
            ])
        )
        st.plotly_chart(fig_success, use_container_width=True)
    
    with col2:
        # График по категориям
        category_counts = df.groupby('category', as_index=False).agg({
            'satisfaction': ['count', lambda x: (x == 1).mean() * 100]
        })
        category_counts.columns = ['category', 'count', 'success_rate']
        
        fig_categories = px.bar(
            category_counts,
            x='category',
            y='count',
            color='success_rate',
            title='Распределение запросов по категориям',
            labels={
                'category': 'Категория',
                'count': 'Количество запросов',
                'success_rate': 'Успешность (%)'
            },
            color_continuous_scale=['red', 'yellow', 'green']
        )
        st.plotly_chart(fig_categories, use_container_width=True)
    
    # Анализ подкатегорий для учебных запросов
    study_df = df[df['category'] == 'Учеба']
    if not study_df.empty:
        st.write("### Анализ учебных запросов")
        subcategory_stats = study_df.groupby('subcategory', as_index=False).agg({
            'satisfaction': ['count', lambda x: (x == 1).mean() * 100]
        })
        subcategory_stats.columns = ['subcategory', 'count', 'success_rate']
        
        fig_subcategories = px.bar(
            subcategory_stats,
            x='subcategory',
            y='count',
            color='success_rate',
            title='Распределение учебных запросов по подкатегориям',
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
    
    # Последние запросы
    st.write("### Последние запросы")
    if len(df) > 0:
        recent_requests = df.sort_values('timestamp', ascending=False).head(10)
        recent_requests['status'] = recent_requests['satisfaction'].map({1: '✅ Успешно', 0: '❌ Ошибка'})
        st.dataframe(
            recent_requests[['timestamp', 'category', 'subcategory', 'query', 'status']].reset_index(drop=True),
            hide_index=True
        )
    else:
        st.info("Нет данных для отображения")

def show_response_time_analysis(df):
    """Анализ времени ответа"""
    st.write("### ⏱️ Анализ времени ответа")
    
    if len(df) > 0:
        # График распределения времени ответа по часам
        df['hour'] = df['timestamp'].dt.hour
        hourly_stats = df.groupby('hour', as_index=False).agg({
            'response_time': ['mean', 'count']
        })
        hourly_stats.columns = ['hour', 'avg_response_time', 'count']
        
        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(
            x=hourly_stats['hour'],
            y=hourly_stats['count'],
            name='Количество запросов',
            marker_color='lightblue'
        ))
        fig_time.add_trace(go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['avg_response_time'],
            name='Среднее время ответа (сек)',
            yaxis='y2',
            line=dict(color='orange', width=2)
        ))
        
        fig_time.update_layout(
            title='Распределение времени ответа по часам',
            xaxis_title='Час',
            yaxis_title='Количество запросов',
            yaxis2=dict(
                title='Среднее время ответа (сек)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Статистика по времени ответа
        col1, col2 = st.columns(2)
        with col1:
            response_stats = df['response_time'].describe()
            st.write("### 📊 Статистика времени ответа")
            st.write(f"Среднее: {response_stats['mean']:.2f} сек")
            st.write(f"Медиана: {response_stats['50%']:.2f} сек")
            st.write(f"Минимум: {response_stats['min']:.2f} сек")
            st.write(f"Максимум: {response_stats['max']:.2f} сек")
        
        with col2:
            # Распределение времени ответа по категориям
            category_time = df.groupby('category')['response_time'].mean().sort_values(ascending=False)
            st.write("### 📈 Среднее время ответа по категориям")
            for cat, time in category_time.items():
                st.write(f"{cat}: {time:.2f} сек")
    else:
        st.info("Нет данных для анализа")
