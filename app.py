import streamlit as st
from assistant import get_assistant_response  # импортируем функцию из assistant.py

# Настройка страницы
st.set_page_config(page_title="Мой AI Ассистент", page_icon="🤖")

st.title("🤖 Мой AI Ассистент")
st.markdown("Задайте любой вопрос — я постараюсь ответить!")

# Инициализация истории сообщений
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение всех сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Обработка ввода пользователя
if prompt := st.chat_input("Введите ваш вопрос..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 💥 ВОТ ЗДЕСЬ ВЫЗЫВАЕТСЯ АССИСТЕНТ
    response = get_assistant_response(prompt)  # ← Заменили заглушку на реальную функцию

    # Добавляем ответ ассистента
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
