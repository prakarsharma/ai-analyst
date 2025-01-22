import pandas as pd
from typing import Union, Dict, Literal

from models_api.system_prompt import data_analyst
from models_api.function_template import tools
from models_api.gemini_api import chat_request, chat_api_message
from models_api.generate import llm
from models_api.vectorize import vectorDB
from utils.cert import load_wmt_ca_bundle
from utils.logging import logger
from utils.utils import clean
from app.knowledge import analyze_and_retrieve_context
from app.history import history
from app import functions


class chatbot:
    def __init__(self, debug_mode=False, safe_mode=False):
        load_wmt_ca_bundle()
        self.data_analyst = llm(data_analyst, functions=tools)
        self.chat = chat_api_message(warm_start=history)
        # self.chunks_db = vectorDB(name="chunks")

    def answer(self, prompt:str) -> Dict[str, str]:
        self.answer_object = {}
        try:
            logger.info("prompt | %s", prompt)
            knowledge = analyze_and_retrieve_context(prompt)
            logger.info("knowledge | %s", knowledge)
            prompter = lambda role, user_prompt: f"User query: {user_prompt}\n\nAnalysis and context:\n{knowledge}"
            self.chat.append("user", prompt, formatter=prompter)
            while "EOS" not in self.answer_object:
                self.generate_response()
                self.call_any_function()
            return self.answer_object
        except (ValueError, ConnectionError) as err:
            logger.error("%s | %s", type(err).__name__, err.args[0], exc_info=True)
            self.chat.pop()
            raise err

    def generate_response(self, **kwargs):
        # scratch_pad = []
        response_object = self.data_analyst.request(self.chat.messages, **kwargs)
        logger.debug("response object | %s", response_object.json())
        response = chat_request.parse_response(response_object)
        logger.info("response | %s", response)
        # if self.chat.messages[-1]["role"] == "user":
            # while len(self.chat.messages[-1]["parts"]) > 1:
                # self.chat.messages[-1]["parts"].pop()
        # if self.chat.messages[-1]["role"] == "user" and response["mode"] == "text":
            # text = clean(response["response"]).string
            # if text.startswith("<scratch-pad>"):
                # scratch_pad.append(text)
                # self.answer_object["scratch_pad"] = text
        self.chat.append("model", **response)
        # if response["mode"] == "functionCall" or scratch_pad:
        if response["mode"] == "functionCall":
            pass
        else:
            self.answer_object["EOS"] = "EOS"
            self.answer_object["answer"] = response["response"]

    def call_any_function(self, **kwargs):
        response = self.chat.messages[-1]["parts"][0]
        if "functionCall" in response:
            name = response["functionCall"]["name"]
            args = response["functionCall"]["args"]
            function_return_object = getattr(functions, name).__call__(**args, **kwargs)
            if name not in ["table", "plot"]:
                logger.debug("function response object | %s", function_return_object)
                function_response = chat_request.function_response(name, function_return_object)
                logger.info("function response | %s", function_response)
                self.chat.append("function", function_response, mode="functionResponse")
                # if "thoughts" in args:
                    # self.answer_object["scratch-pad"] = args["thoughts"]
                if "query" in args:
                    self.answer_object["SQL"] = args["query"]
            else:
                self.answer_object["EOS"] = "EOS"
                self.answer_object[name] = function_return_object

    def capture(self, mode:str, message):
        logger.info("%s | %s", mode, message)
