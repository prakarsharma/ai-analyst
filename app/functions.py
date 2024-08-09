import pandas as pd
from typing import List, Dict
from functools import lru_cache

from app.knowledge import vectorDB
from utils.config import conf
from utils.utils import (create_vertexai_bigquery_client, 
                         create_element_bigquery_connection)


class bigquery_job:
    def __init__(self, safe_mode:bool=False):
        self.safe_mode = safe_mode
        self.platform = conf["platform"]
        self.create_runner()

    def create_runner(self):
        if self.platform == "vertexai":
            self.runner = create_vertexai_bigquery_client()
        if self.platform == "element":
            self.runner = create_element_bigquery_connection()

    def run(self, query:str) -> List[Dict[str,str]]:
        if not self.safe_mode:
            try:
                return self.runner(query)
            except Exception as err:
                # raise ConnectionError("!bigquery job failure!")
                return {
                    "error": str(err)
                }
        return query


bq = bigquery_job()
metrics_db = vectorDB("metrics")

def get_mapping(query:str, **kwargs) -> List[Dict[str,str]]:
    results = {"mapping": bq.run(query)}
    for record in results["mapping"]:
        if "sbu" in record:
            results["sbu"] = record["sbu"]
            metadata = conf["bigquery"][results["sbu"].lower()]
            metadata.update(get_table_schema(**metadata))
            results.update(metadata)
            if not results["schema"]:
                results["schema"] = get_table_schema(results["table_id"])
            relevant_metrics = find_relevant_metrics(kwargs.get("user_prompt"))
            results.update(relevant_metrics)
            break
    return results

def find_relevant_metrics(prompt:str, 
                          metrics:pd.Series=conf["knowledge"]["documents"]["metrics"]["metric"], 
                          definitions:pd.Series=conf["knowledge"]["documents"]["metrics"]["definition"], 
                          limit:int=3, 
                          **kwargs) -> Dict[str, List[str]]:
    search_result = metrics_db.query(prompt)
    matches = metrics_db.match(search_result, limit)
    relevant_metrics = [f"{metrics.get(int(_id))}: {definitions.get(int(_id))}" for _id in matches]
    supporting_document_matches = find_supporting_documents([definitions.get(int(_id)) for _id in matches])
    supporting_documents = [f"{metrics.get(int(_id))}: {definitions.get(int(_id))}" for _id in supporting_document_matches if _id not in matches]
    return {
        "relevant_metrics": relevant_metrics, 
        "supporting_documents": supporting_documents
    }

def find_supporting_documents(definitions:List[str], limit:int=3) -> List[str]:
    supporting_documents = []
    for _ in definitions:
        search_result = metrics_db.query(_)
        matches = metrics_db.match(search_result, limit)
        supporting_documents.extend(matches)
    return list(set(supporting_documents))

@lru_cache
def get_mapping_table(**kwargs) -> Dict:
    metadata = conf["bigquery"]["mapping"]
    metadata.update(get_table_schema(**metadata))
    return metadata

def get_table_schema(**kwargs) -> List[Dict[str,str]]:
    schema = kwargs.get("schema")
    if isinstance(schema, pd.DataFrame):
        parse_schema = lambda row: {
            "column_name": row["fullname"], 
            "data_type": row["type"], 
            "description": row["description"]
        }
        return {
            "schema": [parse_schema(row) for i, row in schema.iterrows()]
        }
    table_id = kwargs.get("table_id")
    if table_id:
        project_id, dataset, table = kwargs["table_id"].split(".")
        query = f"""
SELECT
    column_name,
    data_type,
    description
FROM
    `{project_id}.{dataset}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
WHERE
    table_name='{table}'
"""
        return {
            "schema": bq.run(query)
        }

def fetch_data(sbu:str, query:str, **kwargs) -> List[Dict[str,str]]:
    return bq.run(query)
