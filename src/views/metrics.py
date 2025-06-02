import streamlit as st

def show_metrics(df):
    """Отображение основных метрик"""
    col1, col2, col3 = st.columns(3)
    with col1:
        # Отображение временного периода первым 
        """
        if len(df) > 0:
            period = f"{df['timestamp'].min().strftime('%H:%M')} - {df['timestamp'].max().strftime('%H:%M')}"
        else:
            period = "Нет данных"
        st.metric("Временной период", period)
        """
        st.metric("Всего запросов", len(df))
        success_rate = (df['satisfaction'] == 1).mean() * 100 if len(df) > 0 else 0
        st.metric("Успешность ответов", f"{success_rate:.1f}%")
    
    with col2:
        if len(df) > 0:
            total_errors = len(df[df['satisfaction'] == 0])
            error_rate = (total_errors / len(df) * 100)
            error_warning = " ⚠️ Высокий уровень ошибок!" if error_rate > 30 else ""
            
            # Расчет процента некорректных ответов
            incorrect_count = len(df[df['error_category'] == 'incorrect_answer'])
            incorrect_rate = (incorrect_count / total_errors * 100) if total_errors > 0 else 0
            incorrect_warning = " ⚠️ Высокий уровень некорректных ответов!" if incorrect_rate > 30 else ""
            
            # Расчет процента галлюцинаций
            hallucination_count = len(df[df['error_category'] == 'hallucination'])
            hallucination_rate = (hallucination_count / total_errors * 100) if total_errors > 0 else 0
            hallucination_warning = " ⚠️ Высокий уровень галлюцинаций!" if hallucination_rate > 30 else ""
            
            # Отображение метрик
            if error_rate > 30:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;">
                        <strong>Количество ошибок:</strong> {total_errors} ({error_rate:.1f}%){error_warning}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.metric("Количество ошибок", 
                         f"{total_errors} ({error_rate:.1f}%)")
            
            if incorrect_rate > 30:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;">
                        <strong>Процент некорректных ответов:</strong> {incorrect_rate:.1f}% от ошибок{incorrect_warning}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.metric("Процент некорректных ответов", 
                         f"{incorrect_rate:.1f}% от ошибок")
            
            if hallucination_rate > 30:
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 0, 0, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;">
                        <strong>Процент галлюцинаций:</strong> {hallucination_rate:.1f}% от ошибок{hallucination_warning}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.metric("Процент галлюцинаций", 
                         f"{hallucination_rate:.1f}% от ошибок", 
                         delta=-hallucination_rate, 
                         delta_color="inverse")
        else:
            # Отображение нулевых метрик при отсутствии данных
            st.metric("Количество ошибок", "0 (0%)")
            st.metric("Процент некорректных ответов", "0% от ошибок")
            st.metric("Процент галлюцинаций", "0% от ошибок")

    with col3:
        if len(df) > 0:
            satisfied_count = len(df[df['satisfaction'] == 1])
            unsatisfied_count = len(df[df['satisfaction'] == 0])
        else:
            satisfied_count = 0
            unsatisfied_count = 0
        
        st.metric("Удовлетворенные ответы", f"{satisfied_count} (👍)")
        st.metric("Неудовлетворенные ответы", f"{unsatisfied_count} (👎)")
