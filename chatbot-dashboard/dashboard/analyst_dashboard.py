import streamlit as st
from components.metrics import show_key_tech_metrics
from components.charts import plot_user_activity, plot_success_rates
from utils.db import load_data

def render():
    st.title("📊 Аналитический дашборд")
    st.markdown("Подробная аналитика для разработчиков и преподавателей")

    data = load_data()
    if data.empty:
        st.warning("Нет данных для отображения.")
        return

    selected_date = st.select_slider("Выберите дату", options=sorted(data["date"].unique()))
    filtered = data[data["date"] == selected_date]

    show_key_tech_metrics(filtered)

    st.altair_chart(plot_user_activity(data), use_container_width=True)
    #st.altair_chart(plot_topics(data), use_container_width=True)
    st.altair_chart(plot_success_rates(data), use_container_width=True)

    if st.checkbox("📄 Показать полные данные"):
        st.dataframe(data, use_container_width=True)