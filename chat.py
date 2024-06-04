
import re
import pandas as pd
import streamlit as st

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery

import prompts

bq_clnt = bigquery.Client(project="wmt-mtech-assortment-ml-prod")

st.header("Chat with an AI Markdown analyst 🤖 💬")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question on Markdown..."}]

@st.cache_resource(show_spinner=True)
def load():
    sys_prom = prompts.generate_few_shot_prompt()
    with st.spinner(text="Loading chat..."):
        vertexai.init(project="wmt-mtech-assortment-ml-prod", location="us-central1")
        model = GenerativeModel("gemini-1.0-pro-002", system_instruction=[sys_prom])
        chat = model.start_chat()
        return chat

chat_model = load()
gen_conf = {"max_output_tokens": 2048, "temperature": 0.2, "top_p": 1}

prom = st.chat_input("Your question...")
if prom: # prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prom})

for message in st.session_state.messages: # display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Working..."):
            prom = prompts.generate_prompt(prom)
            response = chat_model.send_message([prom], generation_config=gen_conf)
            answer = response.to_dict()['candidates'][0]['content']['parts'][0]['text']
            query = re.findall("```sql( .*?)```", answer)[0].strip().strip('\n').strip()
            out = f"""```sql
            {query}
            """ # add markdown to pretty print the SQL
            st.write("running query... 🏃‍➡️")
            st.write(out)
            try:
                records = bq_clnt.query(query).result().to_dataframe()
            except Exception as e:
                st.write("⚠️ uh oh! BigQuery gave an error ⛔️")
                raise e
            st.write(records)
            message = {"role": "assistant", "content": out}
            st.session_state.messages.append(message) # add response to message history
