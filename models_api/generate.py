from requests import request, models
from typing import List, Dict

from models_api.gemini_api import chat_request


class llm:
    def __init__(self, config:Dict, api_key:str, system_prompt:str, **kwargs):
        self.name:str = config["llm"]["name"]
        self.gateway_url:str = config["llm"]["gateway_url"]
        self.headers: Dict[str, str] = {"X-Api-Key": api_key}
        self.body = chat_request(self.name, system_prompt, **kwargs)

    def request(self, chat_messages:List[Dict]) -> models.Response:
        payload:Dict = self.body.payload(chat_messages)
        try:
            response:models.Response = request("POST", 
                                               self.gateway_url, 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return response
                    
                
