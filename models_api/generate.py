from requests import request, models
from typing import List, Dict

from models_api.gemini_api import chat_request


class llm:
    def __init__(self, config:Dict, system_prompt:str, api_key:str):
        self.name:str = config["llm"]["name"]
        self.gateway_url:str = config["llm"]["gateway_url"]
        self.headers: Dict[str, str] = {"X-Api-Key": api_key}
        self.body = chat_request(self.name, system_prompt)

    def request(self, chat_messages:List[Dict]) -> str:
        payload:Dict = self.body.payload(chat_messages)
        response:models.Response = request("POST", 
                                           self.gateway_url, 
                                           headers=self.headers, 
                                           json=payload)
        return chat_request.parse_response(response)
