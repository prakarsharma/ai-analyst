import os
import streamlit as st


def load_wmt_llm_gateway_secret():
    os.environ['API_KEY'] = st.secrets.llm_gateway.api_key