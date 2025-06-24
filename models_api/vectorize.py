import os
import shutil
import time
import pandas as pd
import numpy as np
from scipy.special import softmax
from requests import request, models
from chromadb import (EmbeddingFunction, 
                      Documents, 
                      Embeddings, 
                      Collection, 
                      PersistentClient)
from chromadb.config import Settings
from typing import List, Dict, Optional, Literal, cast

from models_api.embedding_api import embedding_request
from utils.secret import authentication
from utils.config import conf
from utils.logging import logger


class embeddingModel(EmbeddingFunction):
    def __init__(self, task:str="SEMANTIC_SIMILARITY"):
        self.headers:Dict = authentication()
        self.task = task.upper()
        # self.title = title

    def __call__(self, input:Documents) -> Embeddings:
        input_ = "".join(input) # input:Union[str,List[str]]
        self.task = cast(
            Literal[
                "SEMANTIC_SIMILARITY", 
                "RETRIEVAL_QUERY", 
                "RETRIEVAL_DOCUMENT", 
                "CLUSTERING", 
                "QUESTION_ANSWERING"
                ], 
                self.task
            )
        payload:Dict = embedding_request.json(input_, self.task)
        try:
            response:models.Response = request("POST", 
                                               conf["models"]["em"]["gateway_url"], 
                                               headers=self.headers, 
                                               json=payload)
        except Exception as err:
            raise ConnectionError("!API request failure!")
        else:
            return embedding_request.parse_response(response) # type: ignore


class vectorDB:
    def __init__(self, 
                 name:str, 
                 path:str, 
                 embedding_function:Optional[embeddingModel]=None, 
                 distance:str="cosine", 
                 overwrite:bool=False, 
                 **kwargs):
        self.name = name
        self.path = path
        if not embedding_function:
            embedding_function = embeddingModel(task="SEMANTIC_SIMILARITY")
        self.embedding_function = embedding_function
        self.distance = distance
        self.db = self.get_or_create()
        logger.info("Found {} documents", self.n_docs)
        if self.n_docs != 0 and overwrite:
            self.delete()
            self.db = self.get_or_create()

    def get_or_create(self):
        if not os.path.exists(self.path):
            logger.info("Creating persist directory at: {}", self.path)
            os.makedirs(self.path)
            # logger.info("Waiting for the directory to be created")
            # time.sleep(2)
            # logger.info("Setting write permission")
            # os.chmod(self.path, 0o757)
        settings = Settings()
        settings.is_persistent = True
        settings.allow_reset = True
        self.client = PersistentClient(self.path, settings=settings)
        logger.info("Getting or creating vector database: '{}'", self.name)
        db:Collection = self.client.get_or_create_collection(name=self.name, 
                                                             embedding_function=self.embedding_function, 
                                                             metadata={"hnsw:space": self.distance})
        return db

    def delete(self):
        if self.client is not None:
            logger.info("Deleting collection: {}", self.name)
            self.client.delete_collection(name=self.name)
            self.db = None
            logger.info(f"Resetting and removing persistent client at: {self.path}")
            result = self.client.reset()
            self.client.clear_system_cache()
            self.client = None
            logger.info("Removing persist directory")
            shutil.rmtree(self.path)

    @property
    def n_docs(self) -> int:
        if self.db is None:
            raise ValueError("!vector database not created!")
        else:
            return self.db.count()

    def upsert(self, documents:Dict[str,str], embeddings:Optional[List[List[float]]]=None, **metadata):
        for i, doc in documents.items():
            kwargs = {"documents": [doc], "ids": [i]}
            if metadata:
                    kwargs["ids"] = [f"{metadata['metadata']}.{i}"]
                    kwargs["metadatas"] = [metadata] # type: ignore
            if embeddings:
                kwargs["embeddings"] = [embeddings[i]] # type: ignore
            self.db.upsert(**kwargs) # type: ignore

    def _top_matches(self, 
                     document:str, 
                     top_n:Optional[int]=None, 
                     filtering:Literal["F-score-based", "gaussian-mixture-classification"]="F-score-based", 
                     **metadata) -> pd.DataFrame:
        search_result = self.query(document, top_n, **metadata)
        if not search_result:
            raise ValueError("!no search results found!")
        results = vectorDB.tabulate_results(search_result)
        if top_n is None:
            logger.info("Retrieving all relevant chunks with heuristic based filtering")
            results = vectorDB.Filter(results, filtering)
        else:
            logger.info("Retrieving top {} relevant chunks", top_n)
            results = results.iloc[:top_n,:].copy()
        return results

    def top_matches(self, 
                    document:str, 
                    top_n:Optional[int]=None, 
                    filtering:Literal["F-score-based", "gaussian-mixture-classification"]="F-score-based", 
                    **metadata) -> Dict[str, List]:
        matches:pd.DataFrame = self._top_matches(document, top_n, filtering, **metadata)
        return matches.to_dict(orient="list") # type: ignore

    def query(self, 
              query_text:str="", 
              top_n:Optional[int]=None, 
              **metadata) -> Dict[str, List[List]]:
        if not query_text:
            raise ValueError("!query cannot be blank!")
        logger.info("Querying vector database with query: '{}'", query_text.replace("'", "\\'").replace('"', '\\"'))
        kwargs = {
            "query_embeddings": self.embedding_function(query_text), # type: ignore
            "n_results": self.n_docs if top_n is None else top_n, 
            "include": ["distances", "documents"]
        }
        if metadata:
            kwargs["where"] = metadata
        logger.info("Performing similarity search")
        if self.db is None:
            raise ValueError("!vector database not created!")
        else:
            result = self.db.query(**kwargs)
            return result # type: ignore

    @staticmethod
    def tabulate_results(query_result:Dict[str,List[List]]) -> pd.DataFrame:
        results = 1 - pd.DataFrame(query_result["distances"][0], index=query_result["ids"][0], columns=["similarity"])
        results["documents"] = query_result["documents"][0]
        results["nodes"] = results.index.to_series().astype(str)
        return results.reset_index(drop=False)

    @staticmethod
    def Filter(scores:pd.DataFrame, 
               filtering:Literal["F-score-based", "gaussian-mixture-classification"]="F-score-based", 
               return_matching:bool=True) -> pd.DataFrame:
        try:
            N = len(scores)
            scores["probability"] = softmax(scores["similarity"].values)

            logger.info("Filtering based on similarity.")
            filtered = scores.loc[scores["similarity"] > 0.5 , :]
            if len(filtered) > 0:
                logger.info("{} results after filtering.", len(scores))
                scores = filtered.copy()

            if len(scores) > 1:
                logger.info("Filtering based on probability.")
                filtered = scores.loc[scores["probability"] > 1/N, :].copy()
                if len(filtered) > 0:
                    logger.info("{} results after filtering.", len(filtered))
                    scores = filtered.copy()

            if len(scores) > 1:
                if filtering == "F_score_based":
                    logger.info("Filtering based on F-score.")
                    filtered = vectorDB.F_score_based_filter(scores, return_matching)
                    if len(filtered) > 0:
                        logger.info("{} results after filtering.", len(filtered))
                        scores = filtered.copy()

            return scores
        except IndexError as err:
            raise ValueError("!bad vector search response!")

    @staticmethod
    def F_score_based_filter(scores:pd.DataFrame, return_matching:bool=True) -> pd.DataFrame:
        scores = vectorDB.F_score(scores)
        highest_F_score = scores["F"].max()
        if not np.isnan(highest_F_score):
            top_k = scores.loc[scores["F"] == highest_F_score, ["rank"]].iloc[0,0]
            if return_matching:
                scores = scores.loc[scores["rank"] <= top_k,:].copy()
        return scores

    @staticmethod
    def F_score(data:pd.DataFrame) -> pd.DataFrame:
        mean = data["similarity"].mean()
        data["rank"] = data["similarity"].rank(method="first", ascending=False)
        data["reverse_rank"] = (len(data) - data["rank"]).replace(0, pd.NA)
        data["within_sum"] = data["similarity"].cumsum()
        data["within_mean"] = data["within_sum"]/ data["rank"]
        data["without_sum"] = data["similarity"].sum() - data["within_sum"]
        data["without_mean"] = data["without_sum"]/ data["reverse_rank"]
        exp_var_in_grp = data["rank"] * (data["within_mean"] - mean).pow(2)
        exp_var_out_grp = data["reverse_rank"] * (data["without_mean"] - mean).pow(2)
        data["explained_variance"] = exp_var_in_grp + exp_var_out_grp
        cal_unexp_var_in_grp = lambda group: (data.loc[data["rank"] <= group["rank"], "similarity"] - group["within_mean"]).pow(2).sum()
        cal_unexp_var_out_grp = lambda group: (data.loc[data["rank"] > group["rank"], "similarity"] - group["without_mean"]).pow(2).sum()
        unexp_var_in_grp = data.apply(cal_unexp_var_in_grp, axis=1)
        unexp_var_out_grp = data.apply(cal_unexp_var_out_grp, axis=1)
        data["unexplained_variance"] = (unexp_var_in_grp + unexp_var_out_grp)/ (len(data) - 2)
        data["F"] = data["explained_variance"]/ data["unexplained_variance"]
        # data["t"] = data["F"].pow(2)
        return data