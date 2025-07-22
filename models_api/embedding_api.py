from typing import Dict, Literal
from requests import models


class embedding_request:
    """
    This class defines a request to an embedding model API.
    """
    @staticmethod
    def json(document:str, 
             task:Literal["SEMANTIC_SIMILARITY", 
                          "RETRIEVAL_QUERY", 
                          "RETRIEVAL_DOCUMENT", 
                          "CLUSTERING", 
                          "QUESTION_ANSWERING"]) -> Dict:
        """
        Constructs a JSON payload for the embedding request.
        :param document: The document to be embedded.
        :param task: The type of downstream task for which the embedding is intended.
        :return: A dictionary of the JSON payload for the request.
        """
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
        """
        Parses the response from the embedding model.
        :param response_object: The response object from the API call.
        :return: A dictionary containing the embeddings.
        :raises ValueError: If the response contains an error or is corrupt.
        """
        if "error" in response_object.json():
            raise ValueError("!bad gateway response!")
        try:
            return response_object.json()["predictions"][0]["embeddings"]["values"]
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt gateway response!")
