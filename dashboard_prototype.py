import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Заголовок
st.set_page_config(page_title="Анализ качества чат-бота", layout="wide")
st.title("📊 Дашборд анализа качества ответов чат-бота")
st.markdown("Анализ метрик NLP, интентов, CSAT и fallback-интентов.")

# Симуляция данных
np.random.seed(42)
n = 1000
data = pd.DataFrame({
    "Дата": pd.date_range("2025-01-01", periods=n, freq="H"),
    "Пользователь": np.random.randint(1, 300, n),
    "Интент": np.random.choice(["greeting", "faq_shipping", "faq_payment", "fallback"], size=n, p=[0.3, 0.3, 0.3, 0.1]),
    "Confidence": np.round(np.random.uniform(0.6, 0.99, n), 2),
    "CSAT": np.random.choice([1, 2, 3, 4, 5], size=n, p=[0.05, 0.1, 0.2, 0.35, 0.3]),
    "Длина диалога": np.random.poisson(5, n)
})

# Сайдбар с фильтрами
st.sidebar.header("🔎 Фильтры")
date_range = st.sidebar.date_input("Выберите период", [data["Дата"].min(), data["Дата"].max()])
selected_intents = st.sidebar.multiselect("Интенты", data["Интент"].unique(), default=list(data["Интент"].unique()))

filtered = data[
    (data["Дата"] >= pd.to_datetime(date_range[0])) &
    (data["Дата"] <= pd.to_datetime(date_range[1])) &
    (data["Интент"].isin(selected_intents))
]

# Основные метрики
st.subheader("📈 Общая статистика")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Диалогов", len(filtered))
col2.metric("Пользователей", filtered["Пользователь"].nunique())
col3.metric("Ср. длина", f"{filtered['Длина диалога'].mean():.2f} шагов")
col4.metric("Средний CSAT", f"{filtered['CSAT'].mean():.2f} / 5")

# График интентов
st.subheader("🎯 Распределение интентов")
chart1 = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("Интент:N", title="Интент"),
    y=alt.Y("count():Q", title="Количество"),
    color="Интент:N"
).properties(width=700)
st.altair_chart(chart1, use_container_width=True)

# Fallback-интенты
st.subheader("⚠️ Частота fallback-интентов")
fallback_rate = (filtered["Интент"] == "fallback").mean() * 100
st.progress(fallback_rate / 100)
st.write(f"Fallback-интенты составляют **{fallback_rate:.2f}%** от всех обращений.")

# Confidence по интентам
st.subheader("🤖 Распределение Confidence по интентам")
chart2 = alt.Chart(filtered).mark_boxplot().encode(
    x="Интент:N",
    y="Confidence:Q",
    color="Интент:N"
)
st.altair_chart(chart2, use_container_width=True)

# CSAT-график
st.subheader("😊 Оценка удовлетворенности пользователей")
chart3 = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("CSAT:O", title="Оценка"),
    y=alt.Y("count():Q", title="Количество"),
    color="CSAT:O"
)
st.altair_chart(chart3, use_container_width=True)

# Таблица
st.subheader("📄 Примеры диалогов")
st.dataframe(filtered.head(15))

# Кнопка обновления
if st.button("🔁 Обновить данные"):
    st.experimental_rerun()
