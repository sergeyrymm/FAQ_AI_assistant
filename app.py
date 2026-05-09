import streamlit as st

# Настройка заголовка страницы
st.set_page_config(page_title="Мой AI Ассистент", page_icon="🤖")

st.title("🤖 Мой AI Ассистент")
st.markdown("Задайте любой вопрос — я постараюсь ответить!")

# Инициализируем историю сообщений (хранится в памяти браузера, пока открыт сайт)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображаем все предыдущие сообщения из истории
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ждем ввода пользователя
if prompt := st.chat_input("Введите ваш вопрос..."):
    # Добавляем сообщение пользователя в историю и показываем его
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # ⚠️ ЗДЕСЬ БУДЕТ ВАШ АССИСТЕНТ ⚠️
    # Пока что ассистент просто повторяет вопрос (эхо-ответ)
    # Позже вы замените это на вызов вашей функции
    response = f"Вы спросили: {prompt}"
    
    # Добавляем ответ ассистента в историю и показываем его
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)