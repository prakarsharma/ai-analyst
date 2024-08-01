from typing import Dict
from requests import models


class embedding_request:
    def json(document:str, title:str="", task:str="RETRIEVAL_DOCUMENT") -> Dict:
        return {
            "instances": [
                {
                    "task_type": task,
                    "title": title,
                    "content": document
                }
            ]
        }

    def parse_response(response_object:models.Response) -> Dict:
        if "error" in response_object.json():
            raise ValueError("!bad gateway response!")
        try:
            return response_object.json()["predictions"][0]["embeddings"]["values"]
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt gateway response!")
