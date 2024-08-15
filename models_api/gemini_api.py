import os
from datetime import datetime
from requests import models
from typing import List, Dict, Union, Literal, Optional, Callable

from utils.database import records_transaction
from utils.config import conf


class chat_request:
    def __init__(self, system_prompt:str, **kwargs):
        self.system_prompt = system_prompt
        self.functions = kwargs.get("functions")
        self.maxOutputTokens = kwargs.get("maxOutputTokens", 2048)
        self.temperature = kwargs.get("temperature", 0.2)
        self.topP = kwargs.get("topP", 1)

    def get_usage_metadata(response:models.Response):
        try:
            return response.json()["usageMetadata"]
        except KeyError:
            raise ConnectionError("!API request failure!")

    def json(self, chat_messages:List[Dict]) -> Dict:
        model_params = {
            "contents": chat_messages,
            "system_instruction": {
                "parts": [
                    {
                        "text": self.system_prompt
                    }
                ]
            },
            "generation_config": {
                "maxOutputTokens": self.maxOutputTokens,
                "temperature": self.temperature,
                "topP": self.topP
            }
        }
        if self.functions:
            functions = {
                "tools": [
                    {
                        "function_declarations": self.functions
                    }
                ]
            }
            model_params.update(functions)
        return model_params

    def _payload(self, chat_messages:List[Dict], **kwargs) -> Dict:
        model_params = self.json(chat_messages)
        allowed_function_names = kwargs.get("allowed_function_names", [])
        if allowed_function_names:
            config = {
                "tool_config": {
                    "function_calling_config": {
                        "mode": "ANY", 
                        "allowed_function_names": allowed_function_names
                    }
                }
            }
            model_params.update(config)
        return model_params

    def payload(self, chat_messages:List[Dict], **kwargs) -> Dict:
        json = self._payload(chat_messages, **kwargs)
        if os.environ["PLATFORM"] == "vertexai":
            return json
        if os.environ["PLATFORM"] == "element":
            return {
            "model": conf["models"]["llm"]["name"],
            "task": "generateContent",
            "model-params": json
            }

    def parse_response(response_object:models.Response) -> Dict:
        if "error" in response_object.json():
            raise ValueError("!bad gateway response!")
        try:
            record_usage_metadata(chat_request.get_usage_metadata(response_object))
            part:Dict[str,Union[str,Dict]] = response_object.json()["candidates"][0]["content"]["parts"][0]
            mode:Literal["text","functionCall"] = list(part.keys())[0]
            response:Union[str,Dict] = list(part.values())[0]
            return {"response":response, "mode":mode}
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt gateway response!")

    def function_response(function_name:str, response) -> Dict:
        return {
                "name": function_name,
                "response": {
                    "name": function_name,
                    "content": response
                }
            }


class chat_api_message:
    def __init__(self, user_prompt:str=None):
        self._messages = []
        if user_prompt:
            self.append("user", user_prompt)

    def template(role:Literal["user","model","function"], 
                 response:Union[str,Dict], 
                 mode:Literal["text","functionCall","functionResponse"]="text", 
                 formatter:Optional[Callable[[str,str],str]]=lambda role, prompt: prompt) -> Dict:
        return {
            "role": role,
            "parts": {mode: formatter(role, response)}
        }

    def append(self, role:str, response:Union[str,Dict], **kwargs):
        self._messages.append(chat_api_message.template(role, response, **kwargs))

    def get_message(self, role:str, mode:str, i:int):
        try:
            return [msg for msg in self._messages if msg["role"] == role and mode in msg["parts"]][i]
        except IndexError as err:
            return {}

    def pop(self):
        if self._messages:
            self._messages.pop()

    @property
    def messages(self) -> List[Dict]:
        return self._messages


def record_usage_metadata(usage_metadata:Dict):
    model = conf["models"]["llm"]["name"]
    timestamp = str(datetime.now())
    records = [[f"'{model}'", f"'{timestamp}'", f"'{token_counter}'", f"{str(count)}"] for token_counter,count in usage_metadata.items()]
    records_transaction(records, table_name="requested_tokens")
