import streamlit as st

from models_api.prompt_template import gemini_chat_api_message
from models_api.system_prompt import analyst_prompt
from models_api.function_template import data_analysis_manifest
from models_api.gemini_api import chat_request
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.config import conf
from utils.logging import get_logger


class chatbot:
    def __init__(self):
        load_wmt_ca_bundle()
        self.llm = llm(conf, st.secrets.llm_gateway.api_key, analyst_prompt, functions=[data_analysis_manifest])
        self.chat = gemini_chat_api_message()
        self.logger = get_logger()

    def answer(self, prompt):
        try:
            self.logger.info("prompt: {}", prompt)
            self.chat.append("user", prompt)
            response = self.llm.request(self.chat.messages)
            self.logger.info("response: {}", response)
            response_part = chat_request.parse_response(response, response_type="functionCall")
            self.chat.append("model", response_part, response_type="functionCall")
            return response_part
        except (ValueError, ConnectionError) as err:
            self.logger.error("{} : {}", type(err), err.args[0])
            self.chat.pop()
            raise err
