import streamlit as st

# ═══════════════════════════════════════════════════════════════
# 1. НАСТРОЙКА СТРАНИЦЫ (зависит от embed-режима)
# ═══════════════════════════════════════════════════════════════

# Проверяем, открыт ли сайт внутри iframe
is_embedded = "embed" in st.query_params

if is_embedded:
    # Режим для встраивания — убираем всё лишнее
    st.set_page_config(
        page_title="AI Ассистент",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
else:
    # Полноценный режим — обычный сайт
    st.set_page_config(
        page_title="Мой AI Ассистент",
        page_icon="🤖",
        layout="centered"
    )

# ═══════════════════════════════════════════════════════════════
# 2. CSS ДЛЯ СКРЫТИЯ ЭЛЕМЕНТОВ STREAMLIT (только в embed-режиме)
# ═══════════════════════════════════════════════════════════════

if is_embedded:
    hide_streamlit_style = """
        <style>
        /* Скрываем шапку Streamlit */
        header {
            visibility: hidden;
            height: 0;
        }

        /* Скрываем футер */
        footer {
            visibility: hidden;
        }

        /* Скрываем меню в правом верхнем углу (три точки) */
        .stApp > header {
            display: none;
        }

        /* Убираем отступ сверху */
        .main .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }

        /* Скрываем сайдбар (если он откроется) */
        section[data-testid="stSidebar"] {
            display: none;
        }

        /* Делаем чат на всю высоту окна */
        html, body, .stApp {
            height: 100%;
        }

        /* Плавные углы для iframe */
        .stApp {
            border-radius: 16px;
        }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3. ИМПОРТ АССИСТЕНТА
# ═══════════════════════════════════════════════════════════════

from assistant import get_assistant_response

# ═══════════════════════════════════════════════════════════════
# 4. ИНТЕРФЕЙС ЧАТА
# ═══════════════════════════════════════════════════════════════

# Заголовок (разный для разных режимов)
if is_embedded:
    # В embed-режиме показываем минимальный заголовок
    st.markdown("### 🤖 AI Ассистент")
else:
    # В обычном режиме — полноценный заголовок
    st.title("🤖 Мой AI Ассистент")
    st.markdown("Задайте любой вопрос — я постараюсь ответить!")
    st.divider()

# Инициализация истории сообщений (хранится в сессии)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение всех предыдущих сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Обработка ввода пользователя
if prompt := st.chat_input("Введите ваш вопрос..."):
    # Добавляем сообщение пользователя в историю
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Вызываем ассистента
    with st.spinner("Думаю..."):
        response = get_assistant_response(prompt)

    # Добавляем ответ ассистента в историю
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# ═══════════════════════════════════════════════════════════════
# 5. КНОПКА ОЧИСТКИ ИСТОРИИ (только в обычном режиме)
# ═══════════════════════════════════════════════════════════════

if not is_embedded:
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗑️ Очистить историю диалога", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
