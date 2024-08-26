import pandas as pd
from typing import List, Dict

from app.knowledge import embeddingModel, vectorDB
from utils.config import conf


documents = conf["knowledge"]["documents"]["metrics"]
metrics_db = vectorDB(name="metrics", embedding_function=embeddingModel(task="SEMANTIC_SIMILARITY"))
metrics_db.upsert(documents["metric"].tolist(), "metric")

def find_relevant_metrics(prompt:str, **kwargs) -> Dict[str, List[str]]:
    relevant_metrics = {}
    if prompt:
        matches = metrics_db.findall([prompt], metadata="metric")
        if matches:
            relevant_metrics["relevant metrics"] = documents.loc[matches, :].to_dict(orient="records")
            supporting_matches = metrics_db.findall(documents.loc[matches, "definition"].tolist(), metadata="metric")
            if supporting_matches:
                relevant_metrics["supporting information"] = documents.loc[list(set(supporting_matches) - set(matches)), :].to_dict(orient="records")
    return relevant_metrics
