from requests import (request, 
                      models)
from chromadb import (EmbeddingFunction, 
                      Documents, 
                      Embeddings, 
                      Client, 
                      Collection)
from typing import List, Dict

from models_api.embedding_api import embedding_request
from models_api.generate import authentication
from utils.config import conf


class embeddingModel(EmbeddingFunction):
    def __init__(self, title:str=""):
        self.headers:Dict = authentication()
        self.title = title

    def __call__(self, input:Documents) -> Embeddings:
        input_ = "".join(input)
        payload:Dict = embedding_request.json(input_, self.title)
        try:
            response:models.Response = request("POST", 
                                               conf["models"]["embedding"]["gateway_url"], 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return embedding_request.parse_response(response)


def get_or_create_vector_db(name:str, documents:List[str]) -> Collection:
    client = Client()
    db:Collection = client.get_or_create_collection(name=name, embedding_function=embeddingModel(name))
    for i, doc in enumerate(documents):
        db.upsert(documents=doc, ids=str(i))
    return db


class vector_db:
    def __init__(self, name:str):
        documents:List[str] = conf["vector_db"]["documents"][name].split("\n\n")
        self.db = get_or_create_vector_db(name, documents)

    def query(self, query_texts:str="", n_results:int=1):
        try:
            if query_texts:
                return self.db.query(query_texts=query_texts, n_results=n_results)["documents"][0][0]
            return query_texts
        except (KeyError, IndexError) as err:
            raise ValueError("!corrupt vector search response!")
