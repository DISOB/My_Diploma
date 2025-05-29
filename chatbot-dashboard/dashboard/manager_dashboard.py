import streamlit as st
import pandas as pd
from utils.db import load_data
from components.charts import plot_user_activity, plot_success_rates, plot_csat_trend

def render():
    st.title("🌟 Менеджерский дашборд")
    st.markdown("##### Ключевые метрики для оперативного управления.")

    data = load_data()
    if data.empty:
        st.warning("Нет данных для отображения.")
        return

    st.sidebar.header("🔎 Фильтры")
    min_date = data["date"].min()
    max_date = data["date"].max()
    date_range = st.sidebar.date_input("Выбери период", [min_date, max_date])

    if len(date_range) != 2:
        st.warning("Выберите начальную и конечную даты")
        return

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered = data[(data["date"] >= start_date) & (data["date"] <= end_date)]

    st.markdown("### 📊 Ключевые метрики")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📅 DAU", f"{filtered['dau'].mean():.0f}")

    with col2:
        success = filtered['success_rate'].mean()
        st.metric("🤖 Успех бота", f"{success:.1f}%")
        if success < 70:
            st.error("⚠️ Уровень успеха бота ниже 70%")

    with col3:
        unknown = filtered['unknown_answer_rate'].mean()
        st.metric("❓ Неизвестные запросы", f"{unknown:.1f}%")
        if unknown > 30:
            st.warning("⚠️ Процент неизвестных ответов высок")

    with col4:
        csat = filtered['csat_score'].mean()
        st.metric("📈 CSAT", f"{csat:.1f} / 5")
        if csat < 3.5:
            st.error("⚠️ Низкий CSAT")

    st.markdown("---")

    st.markdown("### 📈 Графики")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📅 Ежедневная активность (DAU)**")
        st.altair_chart(plot_user_activity(filtered), use_container_width=True)

    with col2:
        st.markdown("**📊 Статистика бота**")
        st.altair_chart(plot_success_rates(filtered), use_container_width=True)

    st.markdown("### 📉 Тренд CSAT")
    st.altair_chart(plot_csat_trend(filtered), use_container_width=True)

    with st.expander("📄 Показать таблицу с данными"):
        st.dataframe(filtered[[
            "date", "dau", "csat_score", "success_rate", "questions_handled"
        ]], use_container_width=True)