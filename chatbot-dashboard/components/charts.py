import altair as alt
import pandas as pd


def plot_user_activity(df: pd.DataFrame, label_color="#000000"):
    return alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("date:T", title="Дата"),
        y=alt.Y("dau:Q", title="DAU"),
        tooltip=["date", "dau"]
    ).properties(
        height=300,
        title="Активность пользователей"
    ).configure_axis(
        labelColor=label_color,
        titleColor=label_color
    ).configure_title(
        color=label_color
    )


def plot_success_rates(df: pd.DataFrame, label_color="#000000"):
    source = df.melt(id_vars=["date"], value_vars=["success_rate", "unknown_answer_rate"],
                     var_name="Метрика", value_name="Значение")
    return alt.Chart(source).mark_line(point=True).encode(
        x=alt.X("date:T", title="Дата"),
        y=alt.Y("Значение:Q", title="%"),
        color=alt.Color("Метрика:N", scale=alt.Scale(scheme="category10")),
        tooltip=["date", "Метрика", "Значение"]
    ).properties(
        height=300,
        title="Успешные и неизвестные ответы"
    ).configure_axis(
        labelColor=label_color,
        titleColor=label_color
    ).configure_legend(
        labelColor=label_color,
        titleColor=label_color
    ).configure_title(
        color=label_color
    )


def plot_csat_trend(df: pd.DataFrame, label_color="#000000"):
    return alt.Chart(df).mark_line(point=True, color="orange").encode(
        x=alt.X("date:T", title="Дата"),
        y=alt.Y("csat_score:Q", title="CSAT"),
        tooltip=["date", "csat_score"]
    ).properties(
        height=300,
        title="Тренд удовлетворённости (CSAT)"
    ).configure_axis(
        labelColor=label_color,
        titleColor=label_color
    ).configure_title(
        color=label_color
    )
