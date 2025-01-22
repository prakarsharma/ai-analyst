import streamlit as st
from streamlit import session_state as ss

from app.main import chatbot


st.set_page_config(
    page_title="AI analyst",
    page_icon="resources/logo.jpeg",
    layout="wide",
)

st.header("Chat with an AI Data Analyst 🤖 💬")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question on SAO..."}]

with st.expander("Sample questions", expanded=False):
    questions = """
"""
    st.write(questions)

with st.spinner("loading chat... 💬"):
    if 'chatbot' not in ss:
        ss.chatbot = chatbot(debug_mode=True)

def capture_feedback(feedback):
    ss.chatbot.capture("feedback", feedback)
    st.toast("✅feedback received!")

prompt:str = st.chat_input("Your question...")
if prompt: # prompt for user input and save to chat history
    ss.messages.append({"role": "user", "content": prompt})

for message in ss.messages: # display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

if ss.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("running query... 🏃‍➡️"):
            try:
                response = ss.chatbot.answer(prompt)
                if "SQL" in response:
                    with st.expander("Show SQL", expanded=False):
                        st.write(response["SQL"])
                if "table" in response:
                    st.write(response["table"])
                if "plot" in response:
                    st.image(response["plot"])
                if "answer" in response:
                    st.write(response["answer"])
                    ss.messages.append({"role": "assistant", "content": response["answer"]}) # add response to message history
            except (ValueError, ConnectionError) as err:
                st.write("⚠️ uh oh! encountered an error 🚫")
        _, up, down, __ = st.columns([0.01, 0.1, 0.1, 0.79])
        with up:
            st.button(':thumbsup:', on_click=capture_feedback, args=('Positive',), key='thumbsup')
        with down:
            st.button(':thumbsdown:', on_click=capture_feedback, args=('Negative',), key='thumbsdown')
