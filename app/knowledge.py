import pandas as pd
from scipy.special import softmax
from sklearn.metrics.pairwise import cosine_similarity
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
    def __init__(self):
        self.headers:Dict = authentication()
        # self.title = title

    def __call__(self, input:Documents) -> Embeddings:
        input_ = "".join(input) # input:Union[str,List[str]]
        payload:Dict = embedding_request.json(input_)
        try:
            response:models.Response = request("POST", 
                                               conf["models"]["embedding"]["gateway_url"], 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return embedding_request.parse_response(response)


class vectorDB:
    def __init__(self, 
                 name:str, 
                 documents:pd.Series=conf["knowledge"]["documents"]["metrics"]["metric"], 
                 distance:str="cosine"):
        client = Client()
        self.db:Collection = client.get_or_create_collection(name=name, 
                                                             embedding_function=embeddingModel(), 
                                                             metadata={"hnsw:space": distance})
        self.upsert([*documents], name)

    @property
    def n_docs(self) -> int:
        return self.db.count()

    def upsert(self, documents:List[str], name:str):
        _id = self.n_docs
        for i, doc in enumerate(documents):
            self.db.upsert(documents=[doc], ids=[str(_id+i)], metadatas=[{"repository": name}])

    def query(self, query_text:str, top_n:int=0, **metadata) -> Dict[str, List[List]]:
        if query_text:
            kwargs = {
                "query_texts": query_text, 
                "n_results": top_n or self.n_docs, 
                "include": ["embeddings", "distances", "documents"]
            }
            if metadata:
                kwargs.update({"where": metadata})
            result = self.db.query(**kwargs)
            return result
        return query_texts

    def match(self, query_result:Dict[str,List[List]], limit:int=1) -> List[str]:
        try:
            similarities = 1 - pd.Series(query_result["distances"][0], index=query_result["ids"][0])
            # similarities.loc[-1] = 0 # a result equivalent to random noise
            probabilities = pd.Series(softmax(similarities.values), index=query_result["ids"][0])
            matches = probabilities.loc[probabilities > self.p_uniform]
            return matches.index.tolist()[:limit]
        except IndexError as err:
            raise ValueError("!bad vector search response!")

    @property
    def p_uniform(self):
        return 1/ self.n_docs
