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


bq = bigquery_job()

def get_plan_dept_sbu_mapping(plan_id:str="", dept_nbr:str="") -> List[Dict[str,str]]:
    if plan_id:
        query = f"""
SELECT
    dept_nbr,
    sbu
FROM
    {conf['bigquery']['mapping']}
WHERE
    plan_id = {plan_id}
"""
    elif dept_nbr:
        query = f"""
SELECT DISTINCT
    sbu
FROM
    {conf['bigquery']['mapping']}
WHERE
    dept_nbr = {dept_nbr}
"""
    result, = bq.run(query)
    sbu = result["sbu"].lower()
    details = conf["bigquery"]["tables"][sbu]
    return {
        "details": result,
        "sbu_database": {
            "bigquery_table": details["table_id"],
            "data_dictionary": get_sbu_data_dictionary(sbu)
        }
    }
    

def get_sbu_data_dictionary(sbu:str) -> List[Dict[str,str]]:
    schema = conf["bigquery"]["tables"][sbu].get("schema")
    if schema:
        return pd.read_csv().to_dict(orient="records")
    else:
        table_id:str = conf["bigquery"]["tables"][sbu]["table_id"]
        return get_table_schema_from_BQ(table_id)

def get_table_schema_from_BQ(table_id:str) -> List[Dict[str,str]]:
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

def fetch_data(sbu:str, query:str) -> List[Dict[str,str]]:
    return bq.run(query)
