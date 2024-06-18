import streamlit as st

from models_api.prompt_template import system_prompt, streamlit_message, gemini_chat_api_message
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.config import conf
from utils.utils import clean_text, bigquery_client


st.header("Chat with an AI Markdown analyst 🤖 💬")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [streamlit_message("assistant", "Ask me a question on Markdown...")]

@st.cache_resource(show_spinner=True)
def load():
    with st.spinner(text="Loading chat..."):
        load_wmt_ca_bundle()
        chatbot = llm(conf, system_prompt, st.secrets.llm_gateway.api_key)
        chat = gemini_chat_api_message()
        bq_client = bigquery_client()
        return chatbot, chat, bq_client

chatbot, chat, bq_client = load()
prompt:str = st.chat_input("Your question...")
if prompt: # prompt for user input and save to chat history
    st.session_state.messages.append(streamlit_message("user", prompt))
    chat.append("user", prompt)

for message in st.session_state.messages: # display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Working..."):
            response = clean_text(chatbot.request(chat.messages))
            chat.append("assistant", response)
            st.write(response)
            st.session_state.messages.append(streamlit_message("assistant", response)) # add response to message history
