import json
from requests import models
from typing import List, Dict, Union

from models_api.chat_message import chat_api_message
from models_api.utils import record_usage_metadata
from utils.config import conf
from utils.logging import logger

class chat_request:
    """
    This class defines a request to the OpenAI Responses API.
    It provides methods to construct the payload for the API request and parse the response.
    """
    def __init__(self, system_prompt:str, **kwargs):
        """
        Initializes the chat_request with a system prompt and optional parameters.
        :param system_prompt: The system prompt to be used in the request.
        :param kwargs: Additional keyword arguments for the request, such as tools, maxOutputTokens, temperature, and topP.
        :raises ConnectionError: If the usage metadata is not found in the response.
        :raises ValueError: If the response from the LLM API is corrupt or departs from the expected schema.
        """
        self.system_prompt = system_prompt
        self.tools = kwargs.get("tools", [])
        self.maxOutputTokens = kwargs.get("maxOutputTokens", 2048)
        self.temperature = kwargs.get("temperature", 0)
        self.topP = kwargs.get("topP", 0.95)

    @staticmethod
    def get_usage_metadata(response:Dict):
        """
        Extracts usage metadata from the response object.
        :param response: The response object from the LLM API request.
        :return: A dictionary containing usage counters compatible with cost.requested_tokens table.
        :raises ConnectionError: If usage metadata is not found in the response.
        """
        counters = ["input_tokens", "output_tokens"]
        try:
            usage = response["usage"]
            return {counter: usage.get(counter, 0) for counter in counters} # default to 0 if not present
        except KeyError:
            raise ConnectionError("!bad gateway response! Usage metadata not found.")

    def json(self, chat_messages:List[Dict]) -> Dict:
        """
        Constructs the JSON payload for the OpenAI Responses API request and inserts the chat messages.
        :param chat_messages: A list of dictionaries of the chat messages.
        :return: A dictionary of the payload JSON for the API request.
        """
        model_params = {
            "input": chat_messages,
            "instructions": self.system_prompt
            }
        generation_config = {
            "max_output_tokens": self.maxOutputTokens,
            "temperature": self.temperature,
            "top_p": self.topP
            }
        model_params.update(generation_config)
        if self.tools:
            tools = {
                "tools": [
                    {
                        "type": "function",
                        **tool
                    }
                    for tool in self.tools
                    ]
                }
            model_params.update(tools)
        return model_params

    def _payload(self, chat_messages:List[Dict], **kwargs) -> Dict:
        """
        Constructs the payload for the OpenAI Responses API request.
        :param chat_messages: A list of dictionaries of chat messages.
        :param kwargs: Additional keyword arguments for the payload, such as allowed_function_names and response_schema.
        :return: A dictionary of the payload JSON for the API request.
        """
        model_params = self.json(chat_messages)
        allowed_function_names = kwargs.get("allowed_function_names", [])
        if allowed_function_names:
            if len(allowed_function_names) == 1:
                model_params["tool_choice"] = {
                    "type": "function",
                    "name": allowed_function_names[0],
                    }
            else:
                model_params["tool_choice"] = "required"
        response_schema = kwargs.get("response_schema", {})
        if response_schema:
            model_params["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "response_schema",
                    "schema": response_schema,
                    "strict": True,
                    }
                }
        return model_params

    def payload(self, chat_messages:List[Dict], **kwargs) -> Dict:
        """
        Constructs the payload for the OpenAI Responses API request.
        :param chat_messages: A list of dictionaries of chat messages.
        :param kwargs: Additional keyword arguments for the payload.
        :return: A dictionary of the payload JSON for the API request.
        """
        json = self._payload(chat_messages, **kwargs)
        return {
            "model": conf["models"]["llm"]["name"],
            **json
            }

    @staticmethod
    def parse_response(response_object:models.Response) -> Dict:
        """
        Parses the response from the OpenAI Responses API and extracts the relevant content.
        :param response_object: The response object from the LLM API request.
        :return: A dictionary containing the response content and mode.
        """
        response_json = response_object.json()
        response_json_str = json.dumps(response_json, ensure_ascii=True, indent=4)
        if response_json.get("error"):
            err_msg = f""""!bad gateway response!"
            {response_json_str}
            """
            raise ValueError(err_msg)
        try:
            logger.debug("Response object:\n{}", response_json_str)

            record_usage_metadata(chat_request.get_usage_metadata(response_json))

            output = response_json.get("output", [])

            for item in output:
                if item.get("type") == "function_call":
                    arguments = item.get("arguments", "{}")
                    try:
                        args = arguments if isinstance(arguments, dict) else json.loads(arguments)
                    except json.JSONDecodeError:
                        args = {}
                    response:Union[str,Dict] = {
                        "name": item.get("name", ""),
                        "args": args,
                        "call_id": item.get("call_id"),
                    }
                    mode = "functionCall"
                    logger.info("Parsed response part:\n mode: {}\n response: {}", mode, response)
                    return {
                        "mode": mode,
                        "response": response,
                    }

            text_chunks:List[str] = []
            for item in output:
                if item.get("type") == "message":
                    for content_item in item.get("content", []):
                        if content_item.get("type") in ["output_text", "text"] and "text" in content_item:
                            text_chunks.append(content_item.get("text", ""))

            if text_chunks:
                mode = "text"
                response = "\n".join(text_chunks).strip()
                logger.info("Parsed response part:\n mode: {}\n response: {}", mode, response)
                return {
                    "mode": mode,
                    "response": response,
                }

            if response_json.get("output_text"):
                mode = "text"
                response = response_json.get("output_text", "")
                logger.info("Parsed response part:\n mode: {}\n response: {}", mode, response)
                return {
                    "mode": mode,
                    "response": response,
                }

            raise KeyError("No supported output content in response.")
        except (KeyError, IndexError) as err:
            err_msg = f"""!corrupt gateway response!
            {response_json_str}
            """
            raise ValueError(err_msg)

    @staticmethod
    def function_response(function_name:str, response, call_id:str="") -> Dict:
        """
        Constructs a function response schema for the LLM API.
        :param function_name: The name of the function that generated the response.
        :param response: The response content from the function.
        :param call_id: OpenAI function call identifier.
        :return: A dictionary containing the function response object.
        """
        logger.info("Function response object:\n{}", response)
        return {
            "mode": "functionResponse",
            "response": {
                "name": function_name,
                "response": {
                    "name": function_name,
                    "content": response
                }
            },
            "call_id": call_id
        }
