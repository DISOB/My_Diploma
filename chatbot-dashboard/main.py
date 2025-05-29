import streamlit as st
import importlib

st.set_page_config(
    page_title="Менеджерский дашборд",
    layout="wide",
    initial_sidebar_state="expanded"
)

DASHBOARDS = {
    "Менеджерский": "dashboard.manager_dashboard",
    "Аналитический": "dashboard.analyst_dashboard"
}

st.sidebar.title("🧽 Выбор дашборда")
selected = st.sidebar.selectbox("Выберите версию", list(DASHBOARDS.keys()))

module_name = DASHBOARDS[selected]
module = importlib.import_module(module_name)
module.render()