import streamlit as st
import plotly.express as px
from src.utils import COLORS

def show_standard_view(df):
    """Отображение стандартного режима"""
    col1, col2 = st.columns(2)
    with col1:
        # График соотношения успешных/неуспешных ответов
        success_count = len(df[df['error_category'] == 'success'])
        errors_count = len(df[df['error_category'] != 'success'])
        fig_success = px.pie(
            names=['Успешные', 'Ошибки'],
            values=[success_count, errors_count],
            title='Соотношение успешных и неуспешных ответов',
            color_discrete_sequence=[COLORS['success'], COLORS['hallucination']]
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
        # Упрощенный график ошибок
        error_df = df[df['error_category'] != 'success']
        error_counts = error_df['error_category'].value_counts().reset_index()
        error_counts.columns = ['category', 'count']
        fig_errors = px.bar(
            error_counts,
            x='category',
            y='count',
            title='Распределение типов ошибок',
            labels={'category': 'Тип ошибки', 'count': 'Количество'},
            color='category',
            color_discrete_map=COLORS
        )
        st.plotly_chart(fig_errors, use_container_width=True)
    
    # Последние запросы
    st.subheader("Последние запросы")
    simple_df = df[['timestamp', 'query', 'satisfaction']].tail(5)
    simple_df['status'] = simple_df['satisfaction'].map({1: '✅ Успешно', 0: '❌ Ошибка'})
    st.dataframe(simple_df[['timestamp', 'query', 'status']], hide_index=True)
