import pandas as pd
from typing import Union, Dict, Literal

from models_api.system_prompt import senior_analyst_prompt, junior_analyst_prompt
from models_api.function_template import data_analysis_manifest
from models_api.gemini_api import chat_request, chat_api_message
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.secret import load_wmt_llm_gateway_secret
from utils.logging import get_logger
from utils.utils import bigquery_connect
from app.analyst import SQL_generator


class chatbot:
    def __init__(self, debug_mode=False):
        load_wmt_ca_bundle()
        load_wmt_llm_gateway_secret()
        self.senior = llm(senior_analyst_prompt)
        self.junior = llm(junior_analyst_prompt, functions=[data_analysis_manifest])
        self.chat = chat_api_message()
        self.instructions = chat_api_message()
        self.logger = get_logger(debug_mode)
        self.bigquery_client = bigquery_connect()

    def answer(self, prompt:str):
        try:
            senior_response = self.generate_response(self.chat, self.senior, prompt)
            response = senior_response["response"]
            junior_response = self.generate_response(self.instructions, self.junior, response)
            mode = junior_response["mode"]
            if mode == "functionCall":
                response = self.query(**junior_response)
                self.instructions.append("model", **junior_response)
            else:
                self.instructions.pop()
            self.chat.append("model", **senior_response)
            return response
        except (ValueError, ConnectionError) as err:
            self.logger.error("%s | %s", type(err).__name__, err.args[0], exc_info=True)
            self.chat.pop()
            self.instructions.pop()
            raise err

    def generate_response(self, chat:chat_api_message, model:llm, prompt:str):
        self.logger.info("prompt | %s", prompt)
        chat.append("user", prompt)
        response_object = model.request(chat.messages)
        self.logger.debug("response object | %s", response_object.json())
        response = chat_request.parse_response(response_object)
        self.logger.info("response | %s", response)
        return response

    def query(self, response:Dict, mode:Literal["text","functionCall"]="functionCall") -> pd.DataFrame:
        query = SQL_generator(response).generate()
        self.logger.info("SQL | %s", query)
        return self.bigquery_client.run(query)
