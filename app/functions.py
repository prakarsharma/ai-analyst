import pandas as pd
from typing import List, Dict
from functools import lru_cache

from app.knowledge import vector_db
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
                raise ConnectionError("!bigquery job failure!")
        return query


bq = bigquery_job()
metrics_db = vector_db("metrics")

def get_mapping(query:str, **kwargs) -> List[Dict[str,str]]:
    results = {"mapping": bq.run(query)}
    for record in results["mapping"]:
        if "sbu" in record:
            results["sbu"] = record["sbu"]
            results["table_id"] = conf["bigquery"][results["sbu"].lower()]['table_id']
            results["schema"] = conf["bigquery"][results["sbu"].lower()]["schema"]
            if not results["schema"]:
                results["schema"] = get_table_schema(results["table_id"])
            results["relevant_metrics"] = metrics_db.query(kwargs.get("user_prompt", ""))
            break
    return results

@lru_cache
def get_mapping_table(table_id:str=conf["bigquery"]["mapping"]['table_id'], **kwargs) -> Dict:
    return {
        "table_id": table_id, 
        "schema": get_table_schema(table_id)
    }

def get_table_schema(table_id:str, **kwargs) -> List[Dict[str,str]]:
    project_id, dataset, table = table_id.split(".")
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
    return bq.run(query)

def fetch_data(sbu:str, query:str, **kwargs) -> List[Dict[str,str]]:
    return bq.run(query)
