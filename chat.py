import streamlit as st

from models_api.prompt_template import few_shot, streamlit_message, gemini_chat_api_message
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.config import conf
from utils.utils import clean, bigquery_connect

st.set_page_config(
    page_title="AI analyst",
    page_icon="conf['streamlit']['icon']",
    layout="wide",
)

st.header("Chat with an AI Markdown analyst 🤖 💬")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [streamlit_message("assistant", "Ask me a question on Markdown...")]

with st.expander("Sample questions:", expanded=True):
    st.write(
        """
        - What is the average discount for the plan no. 3852025?
        - Give me the avg discount and avg expected STR by gate. Plan no. 3780638.
        - Summary statistics plan 3852025.
        - Consider plan 3780638: what's the distribution by discount?
        - Consider plans run in the last week. What was the avg STR by target STR?
        - Any question which is a combination of the above.
    """
    )

@st.cache_resource(show_spinner=True)
def load():
    with st.spinner(text="Loading chat..."):
        load_wmt_ca_bundle()
        chatbot = llm(conf, few_shot().system_prompt, st.secrets.llm_gateway.api_key)
        chat = gemini_chat_api_message()
        bq_client = bigquery_connect()
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
            response = clean(chatbot.request(chat.messages)).string
            chat.append("assistant", response)
            st.write("running query... 🏃‍➡️")
            try:
                result = bq_client.run(response)
            except Exception as e:
                st.write("⚠️ uh oh! BigQuery gave an error ⛔️")
                raise e
            st.write(result)
            st.session_state.messages.append(streamlit_message("assistant", response)) # add response to message history
