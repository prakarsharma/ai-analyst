import pandas as pd
from typing import Union, Dict, Literal

from models_api.system_prompt import system_prompt
from models_api.function_template import tools
from models_api.gemini_api import (chat_request, 
                                   chat_api_message)
from models_api.generate import llm
from utils.cert import load_wmt_ca_bundle
from utils.logging import get_logger
from app.metrics import find_relevant_metrics
from app import functions


class chatbot:
    def __init__(self, debug_mode=False, safe_mode=False):
        load_wmt_ca_bundle()
        self.ba = llm(system_prompt, functions=tools)
        self.chat = chat_api_message()
        self.logger = get_logger(debug_mode)

    def answer(self, prompt:str) -> Dict[str, str]:
        try:
            self.logger.info("prompt | %s", prompt)
            relevant_metrics = find_relevant_metrics(prompt)
            self.logger.info("relevant metrics | %s", relevant_metrics)
            self.chat.append("user", prompt, formatter=lambda role, user_prompt: f"{user_prompt}\n\n{relevant_metrics}")
            self.generate_response(allowed_function_names=["get_markdown_table"])
            self.call_any_function()
            while True:
                EOS = self.generate_response()
                if EOS:
                    last_function_call = self.chat.get_message("model", "functionCall", -1).get("parts", {}).get("functionCall", {})
                    query = last_function_call.get("args", {}).get("query", "") if last_function_call.get("name", "") == "fetch_data" else ""
                    return {
                        "SQL": query, 
                        "answer": EOS
                    }
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


    def call_any_function(self, **kwargs):
        response = self.chat.messages[-1]["parts"]
        if "functionCall" in response:
            name = response["functionCall"]["name"]
            function_return_object = getattr(functions, name).__call__(**response["functionCall"]["args"], **kwargs)
            self.logger.debug("function response object | %s", function_return_object)
            function_response = chat_request.function_response(name, function_return_object)
            self.logger.info("function response | %s", function_response)
            self.chat.append("function", function_response, mode="functionResponse")

    def capture(self, mode:str, message):
        self.logger.info("%s | %s", mode, message)
