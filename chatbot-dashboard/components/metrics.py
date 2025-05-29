import streamlit as st

def show_key_tech_metrics(df):
    st.subheader("🧰 Ключевые технические метрики")
    col1, col2, col3 = st.columns(3)
    col1.metric("DAU", df["dau"].iloc[0])
    col2.metric("Среднее время ответа", f"{df['avg_response_time_ms'].iloc[0]} мс")
    col3.metric("CSAT", f"{df['csat_score'].iloc[0]} / 5")

def show_key_edu_metrics(df):
    st.subheader("🎓 Академические метрики")
    col1, col2, col3 = st.columns(3)
    col1.metric("Студенты DAU", df["unique_students_dau"].iloc[0])
    col2.metric("Вопросов обработано", df["questions_handled"].iloc[0])
    col3.metric("Удовлетворённость", f"{df['csat_score'].iloc[0]} / 5")