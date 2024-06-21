from requests import models
from typing import List, Dict

from models_api.prompt_template import gemini_chat_api_message


class chat_request:
    def __init__(self, model_name:str, system_prompt:str):
        self.model_name = model_name
        self.system_prompt = system_prompt

    def payload(self, chat_messages:List[Dict]) -> Dict:
        return {
            "model": "gemini-1.0-pro",
            "task": "generateContent",
            "model-params": {
                "contents": chat_messages,
                "system_instruction": {
                    "parts": [
                        {
                            "text": self.system_prompt
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

    def parse_response(response:models.Response) -> str:
        if "error" in response:
            raise ValueError("!bad gateway response!")
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt gateway response!")
        