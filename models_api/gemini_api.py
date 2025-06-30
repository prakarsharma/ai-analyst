import os
import json
from datetime import datetime
from requests import models
from typing import List, Dict, Union, Literal, Callable

from utils.database import Database
from utils.config import conf
from utils.logging import logger


class chat_request:
    def __init__(self, system_prompt:str, **kwargs):
        self.system_prompt = system_prompt
        self.tools = kwargs.get("tools", [])
        self.maxOutputTokens = kwargs.get("maxOutputTokens", 2048)
        self.temperature = kwargs.get("temperature", 0)
        self.topP = kwargs.get("topP", 0.95)

    @staticmethod
    def get_usage_metadata(response:Dict):
        counters = ["promptTokenCount", "candidatesTokenCount", "totalTokenCount"]
        try:
            usage_metadata = response["usageMetadata"]
            return {counter: usage_metadata.get(counter, 0) for counter in counters} # default to 0 if not present # candidate toke counter is absent if the LLM generates an empty string
        except KeyError:
            raise ConnectionError("!bad gateway response! Usage metadata not found.")

    def json(self, chat_messages:List[Dict]) -> Dict:
        model_params = {
            "contents": chat_messages,
            "system_instruction": {
                "parts": [
                    {
                        "text": self.system_prompt
                    }
                ]
            }
        }
        generation_config = {
            "responseModalities": ["TEXT"], 
            "maxOutputTokens": self.maxOutputTokens, 
            "temperature": self.temperature, 
            "topP": self.topP
        }
        model_params.update({"generation_config": generation_config})
        safety_setings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT", 
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", 
                "threshold": "BLOCK_NONE"
            }
        ]
        model_params.update({"safetySettings": safety_setings})
        if self.tools:
            tools = {
                "tools": [
                    {
                        "function_declarations": self.tools
                    }
                ]
            }
            model_params.update(tools)
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
        response_schema = kwargs.get("response_schema", [])
        if response_schema:
            generation_config = {
                "responseMimeType": "application/json",
                "responseSchema": response_schema
            }
            model_params["generation_config"].update(generation_config)
        return model_params

    def payload(self, chat_messages:List[Dict], **kwargs) -> Dict:
        """
        Constructs the payload for the LLM API request based on the chat messages and additional parameters.
        :param chat_messages: A list of dictionaries of chat messages.
        :param kwargs: Additional keyword arguments for the payload.
        :return: A dictionary representing the payload JSON for the API request.
        """
        json = self._payload(chat_messages, **kwargs)
        if os.environ["PLATFORM"] == "vertexai":
            return json
        elif os.environ["PLATFORM"] == "element":
            return {
            "model": conf["models"]["llm"]["name"],
            "task": "generateContent",
            "model-params": json
            }
        else:
            err_msg = f"""!unknown platform!
            {os.environ["PLATFORM"]}
            Please set the PLATFORM environment variable to either 'vertexai' or 'element'."""
            raise NotImplementedError(err_msg)

    @staticmethod
    def parse_response(response_object:models.Response) -> Dict:
        """
        Parses the response from the LLM API and extracts the relevant content.
        :param response_object: The response object from the LLM API request.
        :return: A dictionary containing the response content and mode.
        """
        response_json = response_object.json()
        response_json_str = json.dumps(response_json, ensure_ascii=True, indent=4)
        if "error" in response_json:
            err_msg = f""""!bad gateway response!"
            {response_json_str}
            """
            raise ValueError(err_msg)
        try:
            logger.debug("Response object:\n{}", response_json_str)

            record_usage_metadata(chat_request.get_usage_metadata(response_json))

            part:Dict[str,Union[str,Dict]] = response_json["candidates"][0]["content"]["parts"][0]

            for mode in ["text","functionCall"]:
                if mode in part:
                    response:Union[str,Dict] = part.get(mode, "")
                    break
            logger.info("Parsed response part:\n mode: {}\n response: {}", mode, response)
            return {
                "mode": mode, 
                "response": response
                }
        except (KeyError, IndexError) as err:
            err_msg = f"""!corrupt gateway response!
            {response_json_str}
            """
            raise ValueError(err_msg)

    @staticmethod
    def function_response(function_name:str, response) -> Dict:
        logger.info("Function response object:\n{}", response)
        return {
            "mode": "functionResponse",
            "response": {
                "name": function_name,
                "response": {
                    "name": function_name,
                    "content": response
                }
            }
        }


class chat_api_message:
    def __init__(self, user_prompt:str="", warm_start:List[Dict]=[]):
        self._messages = []
        self._messages += warm_start
        if user_prompt:
            self.append("user", user_prompt)

    @staticmethod
    def template(role:Literal["user", 
                              "model", 
                              "function"], 
                 response:Union[str,Dict], 
                 mode:Literal["text", 
                              "functionCall", 
                              "functionResponse"]="text", 
                 formatter:Callable[[str,Union[str,Dict]],Union[str,Dict]]=lambda role, prompt: prompt, 
                 attached_files:List=[], 
                 **kwargs) -> Dict:
        return {
            "role": role,
            "parts": [
                {
                    mode: formatter(role, response)
                }
            ] +\
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
               role:Literal["user", 
                            "model", 
                            "function"], 
               response:Union[str,Dict], 
               **kwargs):
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

    def __str__(self) -> str:
        return json.dumps(self.messages, ensure_ascii=True, indent=4)


def record_usage_metadata(usage_metadata:Dict, table_name:str="cost.requested_tokens"):
    logger.debug("Persisting LLM API usage metadata to '{}'", table_name)
    db = Database(table_name)
    model = conf["models"]["llm"]["name"]
    timestamp = str(datetime.now())
    records = [
        [
            f"'{model}'", 
            f"'{timestamp}'", 
            f"'{token_counter}'", 
            f"{str(count)}"
        ] for token_counter,count in usage_metadata.items()
    ]
    logger.debug("Inserting records:\n{}", "\n".join([", ".join(record) for record in records]))
    db.records_transaction(records)