import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from src.utils import COLORS

def show_developer_view(df):
    """Отображение режима разработчика"""
    tab1, tab2, tab3 = st.tabs(["📊 Категории ответов", "📈 Временной анализ", "📝 Анализ текста"])
    
    with tab1:
        _show_categories_tab(df)
    
    with tab2:
        _show_time_analysis_tab(df)
    
    with tab3:
        _show_text_analysis_tab(df)
    
    # Полные данные
    st.divider()
    st.subheader("📋 Детальные данные")
    st.dataframe(df)
    
    # Экспорт
    st.download_button(
        "📥 Скачать данные (CSV)",
        df.to_csv(index=False).encode('utf-8'),
        "log_analysis.csv",
        "text/csv",
        key='download-csv-dev'
    )

def _show_categories_tab(df):
    """Вкладка с распределением категорий"""
    category_counts = df['error_category'].value_counts()
    fig_categories = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title='Детальное распределение ответов по категориям',
        color=category_counts.index,
        color_discrete_map=COLORS
    )
    fig_categories.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<br>".join([
            "Категория: %{label}",
            "Количество: %{value}",
            "Процент: %{percent}"
        ])
    )
    st.plotly_chart(fig_categories, use_container_width=True)

def _show_time_analysis_tab(df):
    """Вкладка с временным анализом"""
    st.subheader("📈 Временной анализ активности")
    
    # Добавляем временные компоненты для анализа
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date
    
    # График активности по часам
    hourly_stats = df.groupby('hour').agg({
        'satisfaction': ['count', 'mean']
    }).reset_index()
    hourly_stats.columns = ['hour', 'total_requests', 'success_rate']
    
    _show_hourly_activity(hourly_stats)
    _show_error_heatmap(df)
    _show_time_stats(hourly_stats)

def _show_hourly_activity(hourly_stats):
    """График почасовой активности"""
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Bar(
        x=hourly_stats['hour'],
        y=hourly_stats['total_requests'],
        name='Количество запросов',
        marker_color='#636EFA'
    ))
    fig_hourly.add_trace(go.Scatter(
        x=hourly_stats['hour'],
        y=hourly_stats['success_rate'],
        name='Успешность',
        yaxis='y2',
        line=dict(color='#00CC96', width=3)
    ))
    
    fig_hourly.update_layout(
        title='Распределение запросов и успешности по часам',
        xaxis_title='Час',
        yaxis_title='Количество запросов',
        yaxis2=dict(
            title='Процент успешности',
            overlaying='y',
            side='right',
            range=[0, 1]
        ),
        hovermode='x unified'
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

def _show_error_heatmap(df):
    """Тепловая карта ошибок"""
    col1, col2 = st.columns([2, 1])
    with col1:
        errors_by_time = df[df['satisfaction'] == 0].groupby(['date', 'hour']).size().reset_index()
        errors_by_time.columns = ['date', 'hour', 'count']
        
        fig_heatmap = px.density_heatmap(
            errors_by_time,
            x='hour',
            y='date',
            z='count',
            title='Тепловая карта ошибок',
            labels={'hour': 'Час', 'date': 'Дата', 'count': 'Количество ошибок'},
            color_continuous_scale='Viridis'
        )
        fig_heatmap.update_layout(
            xaxis_title='Час дня',
            yaxis_title='Дата'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

def _show_time_stats(hourly_stats):
    """Статистика по времени"""
    with st.container():
        st.subheader("📊 Статистика по часам")
        peak_hour = hourly_stats.loc[hourly_stats['total_requests'].idxmax()]
        best_hour = hourly_stats.loc[hourly_stats['success_rate'].idxmax()]
        st.markdown(f"""
            #### Пиковая активность
            🕐 **Час:** {int(peak_hour['hour']):02d}:00
            📊 **Запросов:** {int(peak_hour['total_requests'])}
            ✅ **Успешность:** {peak_hour['success_rate']:.1%}
            
            #### Лучшая производительность
            🕐 **Час:** {int(best_hour['hour']):02d}:00
            📊 **Запросов:** {int(best_hour['total_requests'])}
            ✅ **Успешность:** {best_hour['success_rate']:.1%}
        """)

def _show_text_analysis_tab(df):
    """Вкладка с анализом текста"""
    # Проверяем на NULL значения и конвертируем в строки
    df['query'] = df['query'].fillna('')
    df['response'] = df['response'].fillna('')
    
    # Вычисляем длины строк
    df['query_length'] = df['query'].astype(str).str.len()
    df['response_length'] = df['response'].astype(str).str.len()
    
    # Отфильтровываем нулевые длины
    plot_df = df[
        (df['query_length'] > 0) & 
        (df['response_length'] > 0)
    ].copy()
    
    _show_text_metrics(plot_df)
    _show_length_analysis(plot_df, len(df))

def _show_text_metrics(plot_df):
    """Показать метрики анализа текста"""
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Средняя длина запроса", f"{plot_df['query_length'].mean():.0f} символов")
        st.metric("Медианная длина запроса", f"{plot_df['query_length'].median():.0f} символов")
    with col2:
        st.metric("Средняя длина ответа", f"{plot_df['response_length'].mean():.0f} символов")
        st.metric("Медианная длина ответа", f"{plot_df['response_length'].median():.0f} символов")

def _show_length_analysis(plot_df, total_records):
    """Показать анализ длины текста"""
    # Добавляем информацию об отфильтрованных данных
    valid_records = len(plot_df)
    if total_records != valid_records:
        st.warning(f"Отфильтровано {total_records - valid_records} записей с пустыми запросами или ответами")
    
    fig_lengths = px.scatter(
        plot_df,
        x='query_length',
        y='response_length',
        color='error_category',
        title='Анализ длины запросов и ответов',
        labels={
            'query_length': 'Длина запроса (символов)',
            'response_length': 'Длина ответа (символов)',
            'error_category': 'Категория'
        },
        color_discrete_map=COLORS
    )
    
    # Улучшаем отображение графика
    fig_lengths.update_traces(
        marker=dict(size=8),
        opacity=0.7
    )
    fig_lengths.update_layout(
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            showgrid=True
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            showgrid=True
        ),
        showlegend=True,
        legend=dict(
            title="Категории",
            font=dict(size=12)
        )
    )
    
    st.plotly_chart(fig_lengths, use_container_width=True)
