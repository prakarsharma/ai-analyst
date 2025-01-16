import os
from requests import request, models
from typing import List, Dict

from models_api.gemini_api import chat_request
from utils.secret import authentication
from utils.config import conf
from utils.logging import logger


class llm:
    def __init__(self, system_prompt:str, **kwargs):
        self.headers = authentication()
        self.body = chat_request(system_prompt, **kwargs)

    def request(self, chat_messages:List[Dict], **kwargs) -> models.Response:
        payload:Dict = self.body.payload(chat_messages, **kwargs)
        # logger.debug("payload | %s", payload)
        try:
            response:models.Response = request("POST", 
                                               conf["models"]["llm"]["gateway_url"], 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return response
