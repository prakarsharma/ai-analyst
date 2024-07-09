import streamlit as st
import pandas as pd
from typing import Union, Dict, Literal

from models_api.system_prompt import analyst_prompt
from models_api.function_template import data_analysis_manifest
from models_api.gemini_api import chat_request, chat_api_message
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.config import conf
from utils.logging import get_logger
from utils.utils import bigquery_connect
from app.analyst import SQL_generator


class chatbot:
    def __init__(self):
        load_wmt_ca_bundle()
        self.llm = llm(conf, st.secrets.llm_gateway.api_key, analyst_prompt, functions=[data_analysis_manifest])
        self.chat = chat_api_message()
        self.logger = get_logger()
        self.bigquery_client = bigquery_connect()

    def answer(self, prompt:str):
        try:
            self.logger.info("prompt | %s", prompt)
            self.chat.append("user", prompt)
            response_object = self.llm.request(self.chat.messages)
            response = chat_request.parse_response(response_object)
            self.logger.debug("response | %s", response)
            out = self.generate_response(**response)
            self.chat.append("model", **response)
            return out
        except (ValueError, ConnectionError) as err:
            self.logger.error("%s | %s", type(err).__name__, err.args[0], exc_info=True)
            self.chat.pop()
            raise err

    def generate_response(self, response:Union[Dict,str], mode:Literal["text","functionCall"]="text") -> Union[str, pd.DataFrame]:
        if mode == "functionCall":
            query = SQL_generator(response).generate()
            self.logger.debug("SQL | %s", query)
            return self.bigquery_client.run(query)
        return response
