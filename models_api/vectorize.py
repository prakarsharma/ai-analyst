import pandas as pd
import numpy as np
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
                 embedding_function:Optional[embeddingModel]=None, 
                 distance:str="cosine"):
        # client = Client()
        client = PersistentClient(path=conf["knowledge"]["db"]["path"])
        if not embedding_function:
            embedding_function = embeddingModel(task="SEMANTIC_SIMILARITY")
        self.embedding_function = embedding_function
        self.db:Collection = client.get_or_create_collection(name=name, 
                                                             embedding_function=embedding_function, 
                                                             metadata={"hnsw:space": distance})

    @property
    def n_docs(self) -> int:
        return self.db.count()

    def upsert(self, documents:Dict[str,str], embeddings:Optional[List[List[float]]]=None, **metadata):
        for i, doc in documents.items():
            kwargs = {"documents": [doc], "ids": [i]}
            if metadata:
                kwargs.update({"ids":[f"{metadata['metadata']}.{i}"]})
                kwargs.update({"metadatas": [metadata]})
            if embeddings:
                kwargs.update({"embeddings":[embeddings[i]]})
            self.db.upsert(**kwargs)

    def top_matches(self, document:str, top_n:Optional[int]=None, **metadata) -> List[str]:
        search_result = self.query(document, **metadata)
        if search_result:
            matches = vectorDB.tabulate_results(search_result)
            if top_n is None or top_n > 1:
                matches = vectorDB.match(matches)
            return matches.iloc[:top_n,:].to_dict(orient="list")

    def query(self, 
              query_text:str="", 
              top_n:int=0, 
              embedding_function:Optional[embeddingModel]=None, 
              return_document:bool=False, 
              **metadata) -> Dict[str, List[List]]:
        if query_text:
            if not embedding_function:
                embedding_function = self.embedding_function
            kwargs = {
                "query_embeddings": embedding_function(query_text), 
                "n_results": top_n or self.n_docs, 
                "include": ["distances"]
            }
            if return_document:
                kwargs["include"].append("documents")
            if metadata:
                kwargs.update({"where": metadata})
            result = self.db.query(**kwargs)
            return result

    def tabulate_results(query_result:Dict[str,List[List]]) -> pd.DataFrame:
        sim = 1 - pd.DataFrame(query_result["distances"][0], index=query_result["ids"][0], columns=["similarity"])
        sim["node"] = sim.index.to_series().astype(str)
        return sim.reset_index(drop=False)

    def match(similarities:pd.DataFrame, return_matching:bool=True) -> pd.DataFrame:
        try:
            similarities["probability"] = softmax(similarities["similarity"].values)
            matches = similarities.loc[(similarities["similarity"] > 0.5) &\
                                       (similarities["probability"] > 1/len(similarities)), :].copy()
            if len(matches) > 1:
                matches = vectorDB.group_match(matches)
                highest_Fscore = matches["F"].max()
                if return_matching and not np.isnan(highest_Fscore):
                    group_size = matches.loc[matches["F"] == highest_Fscore, "rank"].iloc[0]
                    matches = matches.loc[matches["rank"] <= group_size,:].copy()
            return matches
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
        return similarities
