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
from typing import List, Dict, Optional

from models_api.embedding_api import embedding_request
from models_api.generate import authentication
from utils.config import conf


class embeddingModel(EmbeddingFunction):
    def __init__(self, task:str):
        self.headers:Dict = authentication()
        self.task = task
        # self.title = title

    def __call__(self, input:Documents) -> Embeddings:
        input_ = "".join(input) # input:Union[str,List[str]]
        payload:Dict = embedding_request.json(input_, self.task)
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
                 embedding_function:embeddingModel, 
                 distance:str="cosine"):
        # client = Client()
        client = PersistentClient(path=conf["knowledge"]["db"]["path"])
        self.db:Collection = client.get_or_create_collection(name=name, 
                                                             embedding_function=embedding_function, 
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
                _matches = self.match(search_result)["index"]
                if _matches:
                    matches += list(set(_matches) - set(matches))
        if matches:
            return [int(_id.lstrip(f"{metadata}.")) for _id in matches]

    def query(self, 
              query_text:str="", 
              top_n:int=0, 
              embedding_function:Optional[embeddingModel]=None, 
              return_document:bool=False, 
              **metadata) -> Dict[str, List[List]]:
        if query_text:
            kwargs = {
                "query_texts": query_text, 
                "n_results": top_n or self.n_docs, 
                "include": ["distances"]
            }
            if embedding_function:
                kwargs.update({"query_embeddings": embedding_function(query_text)})
                kwargs.pop("query_texts")
            if return_document:
                kwargs["include"].append("documents")
            if metadata:
                kwargs.update({"where": metadata})
            result = self.db.query(**kwargs)
            return result

    def match(self, query_result:Dict[str,List[List]], return_matching:bool=True) -> Dict[str,List[str]]:
        if query_result:
            try:
                n = len(query_result["ids"][0])
                similarities = 1 - pd.DataFrame(query_result["distances"][0], index=query_result["ids"][0], columns=["similarity"])
                # similarities.loc[-1] = 0 # a result equivalent to random noise
                similarities["probability"] = softmax(similarities["similarity"].values)
                probable = similarities.loc[similarities["probability"] > 1/n, :].copy()
                matches = vectorDB.group_match(probable.reset_index())
                if return_matching:
                    matches = matches[matches.matching]
                return matches.to_dict(orient="list")
            except IndexError as err:
                raise ValueError("!bad vector search response!")

    def group_match(similarities:pd.DataFrame, match_table:bool=False) -> pd.DataFrame:
        mean = similarities["similarity"].mean()
        similarities["rank"] = similarities["similarity"].rank(method="first", ascending=False)
        similarities["reverse_rank"] = (len(similarities) - similarities["rank"]).replace(0, pd.NA)
        similarities["within_sum"] = similarities["similarity"].cumsum()
        similarities["within_mean"] = similarities["within_sum"]/ similarities["rank"]
        similarities["without_sum"] = similarities["similarity"].sum() - similarities["within_sum"]
        similarities["without_mean"] = similarities["without_sum"]/ similarities["reverse_rank"]
        exp_var_in_grp = similarities["rank"] * (similarities["within_mean"] - mean).pow(2)
        exp_var_out_grp = similarities["reverse_rank"] * (similarities["without_mean"] - mean).pow(2)
        similarities["explained_variance"] = exp_var_in_grp + exp_var_out_grp
        cal_unexp_var_in_grp = lambda group: (similarities.loc[similarities["rank"] <= group["rank"], "similarity"] - group["within_mean"]).pow(2).sum()
        cal_unexp_var_out_grp = lambda group: (similarities.loc[similarities["rank"] > group["rank"], "similarity"] - group["without_mean"]).pow(2).sum()
        unexp_var_in_grp = similarities.apply(cal_unexp_var_in_grp, axis=1)
        unexp_var_out_grp = similarities.apply(cal_unexp_var_out_grp, axis=1)
        similarities["unexplained_variance"] = (unexp_var_in_grp + unexp_var_out_grp)/ (len(similarities) - 2)
        similarities["F"] = similarities["explained_variance"]/ similarities["unexplained_variance"]
        # similarities["t"] = similarities["F"].pow(2)
        highest_F = similarities["F"].max()
        lowest_rank = similarities.loc[similarities["F"] == highest_F, "rank"].tolist()[0]
        similarities["matching"] = similarities["rank"] <= lowest_rank
        return similarities
