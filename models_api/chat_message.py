import os
import json
from typing import List, Dict, Union, Literal, Callable

class gemini_chat_api_message:
    """
    Gemini chat message helper.
    """
    def __init__(self, user_prompt:str="", warm_start:List[Dict]=[]):
        self._messages = []
        self._messages += warm_start
        if user_prompt:
            self.append("user", user_prompt)

    @staticmethod
    def template(role:Literal["user", "model", "function"],
                 response:Union[str,Dict],
                 mode:Literal["text", "functionCall", "functionResponse"]="text",
                 formatter:Callable[[str,Union[str,Dict]],Union[str,Dict]]=lambda role, prompt: prompt,
                 attached_files:List=[],
                 **kwargs) -> Dict:
        payload = formatter(role, response)
        return {
            "role": role,
            "parts": [
                {
                    mode: payload
                }
            ] +
            [
                {
                    "fileData": {
                        "mimeType": "text/plain",
                        "fileUri": file
                    }
                } for file in attached_files
            ]
        }

    def append(self,
               role:Literal["user", "model", "function"],
               response:Union[str,Dict],
               **kwargs):
        self._messages.append(gemini_chat_api_message.template(role, response, **kwargs))

    def get_message(self, role:str, mode:str, i:int):
        try:
            return [msg for msg in self._messages if msg.get("role") == role and mode in msg.get("parts", [{}])[0]][i]
        except IndexError:
            return {}

    def pop(self):
        if self._messages:
            self._messages.pop()

    @property
    def messages(self) -> List[Dict]:
        return self._messages

    def __str__(self) -> str:
        return json.dumps(self.messages, ensure_ascii=True, indent=4)

class openai_chat_api_message:
    """
    OpenAI Responses API chat message helper.
    """
    def __init__(self, user_prompt:str="", warm_start:List[Dict]=[]):
        self._messages = []
        self._messages += warm_start
        if user_prompt:
            self.append("user", user_prompt)

    @staticmethod
    def template(role:Literal["user", "model", "function"],
                 response:Union[str,Dict],
                 mode:Literal["text", "functionCall", "functionResponse"]="text",
                 formatter:Callable[[str,Union[str,Dict]],Union[str,Dict]]=lambda role, prompt: prompt,
                 attached_files:List=[],
                 **kwargs) -> Dict:
        payload = formatter(role, response)

        if mode == "functionCall":
            args = payload.get("args", {}) if isinstance(payload, dict) else {}
            arguments = args if isinstance(args, str) else json.dumps(args)
            return {
                "type": "function_call",
                "name": payload.get("name", "") if isinstance(payload, dict) else "",
                "arguments": arguments,
                "call_id": payload.get("call_id", "") if isinstance(payload, dict) else "",
            }

        if mode == "functionResponse":
            function_response = payload if isinstance(payload, dict) else {}
            call_id = function_response.get("call_id", "")
            output = function_response.get("response", {}).get("content", "")
            if not isinstance(output, str):
                output = json.dumps(output)
            if call_id:
                return {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": output,
                }
            return {
                "role": "tool",
                "content": [
                    {
                        "type": "input_text",
                        "text": output,
                    }
                ],
            }

        mapped_role = "assistant" if role == "model" else role
        content = [
            {
                "type": "input_text",
                "text": str(payload),
            }
        ]
        if attached_files:
            content += [
                {
                    "type": "input_text",
                    "text": f"Attached file URI: {file}",
                } for file in attached_files
            ]
        return {
            "role": mapped_role,
            "content": content,
        }

    def append(self,
               role:Literal["user", "model", "function"],
               response:Union[str,Dict],
               **kwargs):
        self._messages.append(openai_chat_api_message.template(role, response, **kwargs))

    def get_message(self, role:str, mode:str, i:int):
        try:
            if mode == "functionCall":
                messages = [msg for msg in self._messages if msg.get("type") == "function_call"]
                return messages[i]
            if mode == "functionResponse":
                messages = [msg for msg in self._messages if msg.get("type") == "function_call_output" or msg.get("role") == "tool"]
                return messages[i]
            mapped_role = "assistant" if role == "model" else role
            messages = [msg for msg in self._messages if msg.get("role") == mapped_role]
            return messages[i]
        except IndexError:
            return {}

    def pop(self):
        if self._messages:
            self._messages.pop()

    @property
    def messages(self) -> List[Dict]:
        return self._messages

    def __str__(self) -> str:
        return json.dumps(self.messages, ensure_ascii=True, indent=4)

chat_api_message = openai_chat_api_message if os.environ.get("PLATFORM") == "openai" else gemini_chat_api_message
