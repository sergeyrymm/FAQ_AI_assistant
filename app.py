import streamlit as st

is_embedded = "embed" in st.query_params

if is_embedded:
    st.set_page_config(page_title="AI Ассистент", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")
else:
    st.set_page_config(page_title="Мой AI Ассистент", page_icon="🤖")

if is_embedded:
    hide_streamlit_style = """
        <style>
        header {visibility: hidden; height: 0;}
        footer {visibility: hidden;}
        .stApp > header {display: none;}
        .main .block-container {padding-top: 0rem; padding-bottom: 0rem;}
        section[data-testid="stSidebar"] {display: none;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

from assistant import get_assistant_response

if not is_embedded:
    st.title("🤖 Мой AI Ассистент")
    st.markdown("Задайте любой вопрос!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Введите ваш вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = get_assistant_response(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)