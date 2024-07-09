import os
from datetime import datetime
from requests import request, models
from typing import List, Dict

from models_api.gemini_api import chat_request
from utils.database import records_transaction
from utils.config import conf


class llm:
    def __init__(self, system_prompt:str, **kwargs):
        config:Dict = conf
        self.name:str = config["llm"]["name"]
        self.gateway_url:str = config["llm"]["gateway_url"]
        self.headers: Dict[str, str] = {"X-Api-Key": os.environ['API_KEY']}
        self.body = chat_request(self.name, system_prompt, **kwargs)

    def request(self, chat_messages:List[Dict]) -> models.Response:
        payload:Dict = self.body.payload(chat_messages)
        try:
            response:models.Response = request("POST", 
                                               self.gateway_url, 
                                               headers=self.headers, 
                                               json=payload)
            llm.record_usage_metadata(response)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return response

    def record_usage_metadata(response:models.Response):
        timestamp = str(datetime.now())
        try:
            usage_metadata = response.json()["usageMetadata"]
        except KeyError:
            raise ConnectionError("!API request failure!")
        else:
            records = [{"timestamp":f"'{timestamp}'", "token_counter":f"'{token_counter}'", "count":str(count)} for token_counter,count in usage_metadata.items()]
            records_transaction(records)
