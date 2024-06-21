import streamlit as st

from models_api.prompt_template import few_shot, gemini_chat_api_message
from models_api.gemini_api import chat_request
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.config import conf
from utils.utils import clean, bigquery_connect
from utils.logging import get_logger


class chatbot:
    def __init__(self):
        load_wmt_ca_bundle()
        self.llm = llm(conf, few_shot().system_prompt, st.secrets.llm_gateway.api_key)
        self.chat = gemini_chat_api_message()
        self.bq_client = bigquery_connect()
        self.logger = get_logger()

    def answer(self, prompt):
        try:
            self.logger.info("prompt: {}", prompt)
            self.chat.append("user", prompt)
            response = self.llm.request(self.chat.messages)
            response_text = chat_request.parse_response(response)
            self.logger.info("CoT: {}", response_text)
            query = clean(response_text).string
            self.logger.info("SQL: {}", query)
            result = self.bq_client.run(query)
            self.chat.append("model", response_text)
            return result
        except (ValueError, ConnectionError) as err:
            self.logger.error("{} : {}", type(err), err.args[0])
            self.chat.pop()
            raise err
