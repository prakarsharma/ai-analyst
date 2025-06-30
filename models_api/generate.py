import json
from requests import request, models
from typing import List, Dict, Union

from models_api.gemini_api import chat_request, chat_api_message
from utils.secret import authentication
from utils.config import conf
from utils.logging import logger


class llm:
    """
    A class to interact with a Large Language Model (LLM) via an API.
    """
    def __init__(self, system_prompt:str, **kwargs):
        """
        Initializes the LLM with a system prompt and optional parameters.
        :param system_prompt: The system prompt to guide the LLM's responses.
        :param kwargs: Additional keyword arguments for the LLM request.
        """
        self.headers = authentication()
        self.body = chat_request(system_prompt, **kwargs)

    def request(self, chat_messages:List[Dict], **kwargs) -> models.Response:
        """
        Sends a request to the LLM API with the provided chat messages.
        :param chat_messages: A list of dictionaries representing chat messages.
        :param kwargs: Additional keyword arguments for the request.
        :return: The response from the LLM API.
        """
        payload:Dict = self.body.payload(chat_messages, **kwargs)
        try:
            payload_json = json.dumps(payload, indent=4)
            logger.debug("Sending request payload:\n{}", payload_json)
            response:models.Response = request("POST", 
                                               conf["models"]["llm"]["gateway_url"], 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return response

    def generate(self, prompt:str, **kwargs) -> Union[str, Dict]:
        """
        Generate a response from the LLM based on the provided prompt.
        :param prompt: The input prompt for the LLM.
        :param gen_kwargs: Additional keyword arguments for the generation request.
        :return: A dictionary containing the LLM's response.
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty!")
        message = chat_api_message()
        message.append("user", prompt, **kwargs)
        response_object = self.request(message.messages, **kwargs)
        response:str = chat_request.parse_response(response_object)["response"] # type: ignore
        if "response_schema" in kwargs:
            response:dict = json.loads(response) # type: ignore
        return response