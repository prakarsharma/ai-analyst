from requests import models
from typing import List, Dict, Union, Literal


class chat_request:
    def __init__(self, model_name:str, system_prompt:str, **kwargs):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.functions = kwargs.get("functions")
        self.allowed_function_names = kwargs.get("allowed_function_names", [])

    def json(model_name:str, system_prompt:str, chat_messages:List[Dict]) -> Dict:
        return {
            "model": model_name,
            "task": "generateContent",
            "model-params": {
                "contents": chat_messages,
                "system_instruction": {
                    "parts": [
                        {
                            "text": system_prompt
                        }
                    ]
                },
                "generation_config": {
                    "maxOutputTokens": 2048,
                    "temperature": 0.2,
                    "topP": 1
                },
            }
        }

    def payload(self, chat_messages:List[Dict]) -> Dict:
        json = chat_request.json(self.model_name, self.system_prompt, chat_messages)
        if self.functions:
            functions = {
                "tools": [
                {
                    "function_declarations": self.functions
                }
            ]
            }
            json["model-params"].update(functions)
        if self.allowed_function_names:
            config = {
                "tool_config": {
                    "function_calling_config": {
                        "mode": "ANY", 
                        "allowed_function_names": self.allowed_function_names
                    }
                }
            }
            json["model-params"].update(config)
        return json

    def parse_response(response_object:models.Response) -> Dict:
        if "error" in response_object.json():
            raise ValueError("!bad gateway response!")
        try:
            part:Dict[str,Union[str,Dict]] = response_object.json()["candidates"][0]["content"]["parts"][0]
            response_type:Literal["text","functionCall"] = list(part.keys())[0]
            response:Union[str,Dict] = list(part.values())[0]
            return {"response_type":response_type, "response":response}
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt gateway response!")
