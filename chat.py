import streamlit as st
from streamlit import session_state as ss

from app.main import chatbot


st.set_page_config(
    page_title="AI analyst",
    page_icon="resources/logo.jpeg",
    layout="wide",
)

st.header("Chat with an AI Markdown analyst 🤖 💬")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question on Markdown..."}]

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

with st.spinner("loading chat... 💬"):
    if 'chat' not in ss:
        ss.chat = chatbot()

prompt:str = st.chat_input("Your question...")
if prompt: # prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("running query... 🏃‍➡️"):
            try:
                answer = ss.chat.answer(prompt)
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer}) # add response to message history
            except (ValueError, ConnectionError) as err:
                st.write("⚠️ uh oh! encountered an error 🚫")
