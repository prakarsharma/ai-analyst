import pandas as pd
from scipy.special import softmax
from sklearn.metrics.pairwise import cosine_similarity
from requests import (request, 
                      models)
from chromadb import (EmbeddingFunction, 
                      Documents, 
                      Embeddings, 
                      Client, 
                      PersistentClient, 
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
                 distance:str="cosine"):
        # client = Client()
        client = PersistentClient(path=conf["knowledge"]["db"]["path"])
        self.db:Collection = client.get_or_create_collection(name=name, 
                                                             embedding_function=embeddingModel(), 
                                                             metadata={"hnsw:space": distance})

    @property
    def n_docs(self) -> int:
        return self.db.count()

    def upsert(self, documents:List[str], metadata:str):
        for i, doc in enumerate(documents):
            self.db.upsert(documents=[doc], ids=[f"{metadata}.{str(i)}"], metadatas=[{"metadata": metadata}])

    def findall(self, documents:List[str], metadata:str) -> List[str]:
        matches = []
        for doc in documents:
            search_result = self.query(doc, metadata=metadata)
            if search_result:
                _matches = self.match(search_result)
                if _matches:
                    matches += list(set(_matches) - set(matches))
        if matches:
            return [int(_id.lstrip(f"{metadata}.")) for _id in matches]

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

    def match(self, query_result:Dict[str,List[List]]) -> List[str]:
        if query_result:
            try:
                n = len(query_result["ids"][0])
                similarities = 1 - pd.DataFrame(query_result["distances"][0], index=query_result["ids"][0], columns=["similarity"])
                # similarities.loc[-1] = 0 # a result equivalent to random noise
                similarities["probability"] = softmax(similarities["similarity"].values)
                matches = similarities.loc[similarities["probability"] > 1/n, ["similarity"]].copy()
                return matches.index.tolist()
            except IndexError as err:
                raise ValueError("!bad vector search response!")

