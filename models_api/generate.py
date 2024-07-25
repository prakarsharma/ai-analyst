import os
from requests import request, models
from typing import List, Dict

from models_api.gemini_api import chat_request
from utils.secret import (load_wmt_llm_gateway_secret, 
                          load_gcloud_oauth_token)
from utils.config import conf


class llm:
    def __init__(self, system_prompt:str, **kwargs):
        self.headers = llm.authentication()
        self.body = chat_request(system_prompt, **kwargs)

    def request(self, chat_messages:List[Dict], **kwargs) -> models.Response:
        payload:Dict = self.body.payload(chat_messages, **kwargs)
        try:
            response:models.Response = request("POST", 
                                               conf["llm"]["gateway_url"], 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return response

    def authentication() -> Dict[str,str]:
        if conf["platform"] == "vertexai":
            load_gcloud_oauth_token()
            access_token:str = os.environ["ACCESS_TOKEN"]
            return {"Authorization": f"Bearer {access_token}"}
        if conf["platform"] == "element":
            load_wmt_llm_gateway_secret()
            api_key:str = os.environ["API_KEY"]
            return {"X-Api-Key": api_key}
