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
    """Отображение стандартного режима"""
    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← На главную"):
            st.session_state.page = 'main'
            st.rerun()
    
    # Создаем две колонки для графиков
    col1, col2 = st.columns(2)
    
    with col1:
        # График распределения по кампусам
        campus_stats = df.groupby('campus').size().reset_index(name='count')
        total_count = campus_stats['count'].sum()
        # Изменяем способ расчета процентов, чтобы сумма всегда была ровно 100%
        percentages = []
        running_total = 0
        for i, count in enumerate(campus_stats['count']):
            if i == len(campus_stats) - 1:
                # Для последнего элемента берем остаток до 100%
                percentage = 100 - running_total
            else:
                percentage = (count / total_count * 100).round(1)
                running_total += percentage
            percentages.append(percentage)
        
        campus_stats['percentage'] = percentages
        
        fig_campus = px.pie(
            campus_stats,
            values='count',
            names='campus',
            title='Распределение запросов по кампусам',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hover_data=['percentage']
        )
        
        st.plotly_chart(fig_campus, use_container_width=True)
    
    with col2:
        # График распределения ошибок по категориям
        error_df = df[df['satisfaction'] == 0]
        # Добавляем проверку на количество уникальных категорий
        if not error_df.empty and df['category'].nunique() > 1:
            category_errors = error_df.groupby('category').size().reset_index(name='count')
            category_errors['percentage'] = (category_errors['count'] / len(error_df) * 100).round(1)
            
            fig_category_errors = px.pie(
                category_errors,
                values='count',
                names='category',
                title='Распределение неудовлетворенности по категориям',
                color_discrete_sequence=px.colors.qualitative.Set3,
                hover_data=['percentage']
            )
            fig_category_errors.update_traces(
                textposition='inside',
                textinfo='percent'
            )
            st.plotly_chart(fig_category_errors, use_container_width=True)
    
    # Последние запросы
    st.write("### Последние запросы")
    if len(df) > 0:
        # Добавляем фильтр удовлетворенности
        satisfaction_filter = st.selectbox(
            "Фильтр по удовлетворенности",
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
        recent_requests = filtered_df.sort_values(['date', 'question_time'], ascending=[False, False]).head(10)
        
        # Переименовываем колонки и меняем значения в столбце статуса
        display_df = (recent_requests[columns_to_show.keys()]
                     .rename(columns=columns_to_show)
                     .copy())
        
        display_df['Статус'] = display_df['Статус'].map({
            1: '✅ Удовлетворительно',
            0: '❌ Неудовлетворительно'
        })
        
        # Отображаем таблицу
        st.dataframe(
            display_df.reset_index(drop=True),
            hide_index=True
        )
        
        # Добавляем кнопку для скачивания CSV
        st.download_button(
            label="📥 Скачать данные (CSV)",
            data=display_df.to_csv(index=False).encode('utf-8-sig'),
            file_name="chatbot_analysis.csv",
            mime="text/csv",
            key='download-csv'
        )
    else:
        st.info("Нет данных для отображения")

def show_response_time_analysis(df):
    """Анализ времени ответа"""
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("← На главную"):
            st.session_state.page = 'main'
            st.rerun()
    with col_title:
        st.title("⏱️ Анализ времени ответа")

    if len(df) > 0:
        # Добавляем селектор периода только для анализа времени ответа
        time_period = st.selectbox(
            "Группировать по",
            ["Часам", "Дням", "Неделям", "Месяцам"],
            key="time_period_selector"
        )
        
        # Используем период из селектора
        if time_period == "Часам":
            df['period'] = df['timestamp'].dt.hour
            period_name = 'часам'
        elif time_period == "Дням":
            df['period'] = df['timestamp'].dt.date
            period_name = 'дням'
        elif time_period == "Неделям":
            df['period'] = df['timestamp'].dt.isocalendar().week
            period_name = 'неделям'
        else:  # Месяцы
            # Convert Period to string for months
            df['period'] = df['timestamp'].dt.strftime('%Y-%m')
            period_name = 'Месяцам'
        
        # Group and aggregate data
        period_stats = df.groupby('period', as_index=False).agg({
            'response_time': ['mean', 'count']
        })
        period_stats.columns = ['period', 'avg_response_time', 'count']
        
        # Sort values
        period_stats = period_stats.sort_values('period')
        
        # Create figure
        fig_time = go.Figure()
        
        # Add traces
        fig_time.add_trace(go.Bar(
            x=period_stats['period'].astype(str),  # Convert to string
            y=period_stats['count'],
            name='Количество запросов',
            marker_color='lightblue'
        ))
        
        fig_time.add_trace(go.Scatter(
            x=period_stats['period'].astype(str),  # Convert to string
            y=period_stats['avg_response_time'],
            name='Среднее время ответа (сек)',
            yaxis='y2',
            line=dict(color='orange', width=2)
        ))
        
        # Update layout
        fig_time.update_layout(
            title=f'Распределение времени ответа по {period_name}',
            xaxis_title=period_name.capitalize(),
            yaxis_title='Количество запросов',
            yaxis2=dict(
                title='Среднее время ответа (сек)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        # Rotate labels if needed
        if time_period != "Часы":
            fig_time.update_xaxes(tickangle=45)
        
        st.plotly_chart(fig_time, use_container_width=True)
        
        # Статистика по времени ответа
        col1, col2 = st.columns(2)
        with col1:
            response_stats = df['response_time'].describe()
            st.write("### 📊 Статистика времени ответа")
            stats_data = {
                'Метрика': ['Среднее', 'Медиана', 'Минимум', 'Максимум'],
                'Значение': [
                    response_stats['mean'],
                    response_stats['50%'],
                    response_stats['min'],
                    response_stats['max']
                ]
            }
            
            fig_stats = px.bar(
                stats_data,
                x='Метрика',
                y='Значение',
                title='Статистика времени ответа (в секундах)',
                color_discrete_sequence=[COLORS['success']]
            )
            fig_stats.update_traces(
                text=fig_stats.data[0].y.round(2),
                textposition='outside'
            )
            st.plotly_chart(fig_stats, use_container_width=True)
        
        with col2:
            # Распределение времени ответа по категориям
            # Проверяем, выбрана ли конкретная категория
            if df['category'].nunique() > 1:  # если больше одной категории
                category_time = df.groupby('category')['response_time'].mean().sort_values(ascending=True)
                st.write("### 📈 Среднее время ответа по категориям")
                
                fig_category_time = px.bar(
                    x=category_time.values,
                    y=category_time.index,
                    orientation='h',
                    title='Среднее время ответа по категориям',
                    labels={'x': 'Время (сек)', 'y': 'Категория'},
                    color_discrete_sequence=[COLORS['success']]
                )
                fig_category_time.update_traces(
                    text=category_time.values.round(2),
                    textposition='outside'
                )
                st.plotly_chart(fig_category_time, use_container_width=True)
    else:
        st.info("Нет данных для анализа")
