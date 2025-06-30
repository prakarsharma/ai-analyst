from typing import Dict, Literal
from requests import models


class embedding_request:
    @staticmethod
    def json(document:str, 
             task:Literal["SEMANTIC_SIMILARITY", 
                          "RETRIEVAL_QUERY", 
                          "RETRIEVAL_DOCUMENT", 
                          "CLUSTERING", 
                          "QUESTION_ANSWERING"]) -> Dict:
        return {
            "instances": [
                {
                    "task_type": task,
                    "content": document
                }
            ]
        }

    @staticmethod
    def parse_response(response_object:models.Response) -> Dict:
        if "error" in response_object.json():
            raise ValueError("!bad gateway response!")
        try:
            return response_object.json()["predictions"][0]["embeddings"]["values"]
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt gateway response!")
