
import re
import pandas as pd
import streamlit as st

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import bigquery

bq_clnt = bigquery.Client(project="wmt-mtech-assortment-ml-prod")

st.header("Chat with an AI Markdown analyst 🤖 💬")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question on Markdown..."}]

@st.cache_resource(show_spinner=True)
def load():

    table = 'clearance_markdown_ml_prod.vm_final_recommendations_pd'
    schema = ',\n'.join([f"{_[0]} : {_[1]}" for i,_ in pd.read_csv("price_drivers_table.csv", header=None).iterrows()])
    sys_prom = f"""Consider a table named '{table}' with column names and their meanings provided below in a dictionary format enclosed in double backticks:
    ``
    {schema}
    ``
    As data analysis expert, your job is to write a SQL query which can return the output the user expects from this table.
    """

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
            response = chat_model.send_message([prom], generation_config=gen_conf)
            answer = response.to_dict()['candidates'][0]['content']['parts'][0]['text']
            cln_ans = answer.strip().strip('\n').strip() # clean the response
            query = re.sub('^sql', '', cln_ans.strip('`')) # extract SQL from markdown
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
