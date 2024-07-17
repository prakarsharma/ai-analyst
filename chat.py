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

with st.expander("Sample questions:", expanded=False):
    st.write(
        """
        - Plan no. 3800009. What is the avg markdown percent for the items in department 34?
        - What is the str achieved and target str and number of items by gate for the plan?
        - Can you tell me the wt avg markdown and 90th percentile markdown by gate? Same plan.
        - min, max and avg discount and review and created dates for a given plan.
        - Distribution by discount range for a particular plan.
        - Summary of a plan.
        - Plans created last week markdown reason is 'STR achieved'.
        - Markdown reason being infeasible min price, what's the number and average discount for such plans? Filter on plans run this year and show results by week.
        - For the plans run in the 1st week of July which failed to meet budget restrictions, what's the distribution by markdown range?
        - Items which have high markdown and low inventory for a particular plan.
        - Plans whose budget changed in the last 1 week?
        - For plans whose budget changed in the last week has the inventory changed for any items?
        - What is the definition of wt. avg. discount?
        - How does the optimizer work?
        - What are some other kinds of questions you can answer?
    """
    )

with st.spinner("loading chat... 💬"):
    if 'chatbot' not in ss:
        ss.chatbot = chatbot()

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
                answer = ss.chatbot.answer(prompt)
                st.write(answer)
                ss.messages.append({"role": "assistant", "content": answer}) # add response to message history
            except (ValueError, ConnectionError) as err:
                st.write("⚠️ uh oh! encountered an error 🚫")
        _, up, down, __ = st.columns([0.01, 0.1, 0.1, 0.79])
        with up:
            st.button(':thumbsup:', on_click=capture_feedback, args=('Positive',), key='thumbsup')
        with down:
            st.button(':thumbsdown:', on_click=capture_feedback, args=('Negative',), key='thumbsdown')
