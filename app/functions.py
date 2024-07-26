import pandas as pd
from typing import List, Dict

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


def get_available_datasets() -> List[Dict[str,str]]:
    datasets_list = []
    for name, metadata in conf["bigquery"]["tables"].items():
        with open(metadata["annotation"], "r") as f:
            annotation = f.read()
        details = dict(name=name, table_id=metadata["table_id"], annotation=annotation)
        datasets_list.append(details)
    return datasets_list

bq = bigquery_job()

def get_data_dictionary(name:str) -> List[Dict[str,str]]:
    schema = conf["bigquery"]["tables"][name].get("schema")
    if schema:
        return pd.read_csv().to_dict(orient="records")
    else:
        table_id:str = conf["bigquery"]["tables"][name]["table_id"]
        return get_table_schema_from_BQ(table_id)

def get_table_schema_from_BQ(table_id:str) -> List[Dict[str,str]]:
    project_id, dataset, table = table_id.split(".")
    query = f"""SELECT
    column_name,
    data_type,
    description
FROM
    `{project_id}.{dataset}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
WHERE
    table_name='{table}'
"""
    return bq.run(query)

def run_bigquery_job(query:str) -> List[Dict[str,str]]:
    return bq.run(query)

def display_results(results:str):
    return {
        "<EOS>": results
    }
