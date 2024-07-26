import pandas as pd
from typing import Union, Dict, Literal

from models_api.system_prompt import system_prompt
from models_api.function_template import (get_plan_dept_sbu_mapping, 
                                          get_sbu_data_dictionary, 
                                          fetch_data)
from models_api.gemini_api import (chat_request, 
                                   chat_api_message)
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.logging import get_logger
from app import functions


class chatbot:
    def __init__(self, debug_mode=False, safe_mode=False):
        load_wmt_ca_bundle()
        self.ba = llm(system_prompt, functions=[get_plan_dept_sbu_mapping, 
                                                get_sbu_data_dictionary, 
                                                fetch_data])
        self.chat = chat_api_message()
        self.logger = get_logger(debug_mode)

    def answer(self, prompt:str):
        try:
            self.logger.info("prompt | %s", prompt)
            self.chat.append("user", prompt)
            while True:
                EOS = self.generate_response()
                if EOS:
                    return EOS
                self.call_any_function()
        except (ValueError, ConnectionError) as err:
            self.logger.error("%s | %s", type(err).__name__, err.args[0], exc_info=True)
            self.chat.pop()
            raise err

    def generate_response(self, **kwargs):
        response_object = self.ba.request(self.chat.messages, **kwargs)
        self.logger.debug("response object | %s", response_object.json())
        response = chat_request.parse_response(response_object)
        self.logger.info("response | %s", response)
        self.chat.append("model", **response)
        if response["mode"] != "functionCall":
            return response["response"]


    def call_any_function(self):
        response = self.chat.messages[-1]["parts"]
        if "functionCall" in response:
            name = response["functionCall"]["name"]
            function_return_object = getattr(functions, name).__call__(**response["functionCall"]["args"])
            self.logger.debug("function response object | %s", function_return_object)
            function_response = chat_request.function_response(name, function_return_object)
            self.logger.info("function response | %s", function_response)
            self.chat.append("function", function_response, mode="functionResponse")

    def capture(self, mode:str, message):
        self.logger.info("%s | %s", mode, message)
