import os
import yaml
import json
import pandas as pd
from typing import List, Dict, Union

from utils.bq import bigquery_job


def get_env_var(loader, node) -> str:
    """
    Retrieves the value of an environment variable by its name in the yaml node.
    If the environment variable is not set, an empty string is returned.
    """
    name = loader.construct_scalar(node)
    return os.environ.get(name, "")

def concat(loader, node) -> str:
    """
    Concatenates a sequence of strings from a yaml node into a single string.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(_) for _ in seq])

def read_text(loader, node) -> str:
    """
    Reads the contents of a text file specified in the yaml node.
    The path to the file is expected to be a string.
    """
    path = loader.construct_scalar(node)
    with open(path, "r") as f:
        text = f.read()
    return text

def read_csv(loader, node) -> pd.DataFrame:
    """
    Reads a CSV file specified in the yaml node and return it as a pandas DataFrame.
    The path to the CSV file is expected to be a string.
    """
    path = loader.construct_scalar(node)
    dataframe = pd.read_csv(path)
    return dataframe

def read_json(loader, node) -> Union[List,Dict]:
    """
    Reads a JSON file specified in the yaml node and return its contents.
    The path to the JSON file is expected to be a string.
    """
    path = loader.construct_scalar(node)
    with open(path, "r") as f:
        contents = json.loads(f.read())
    return contents

def get_or_read_schema(loader, node) -> Dict:
    """
    Gets or reads the schema of a BigQuery table or a CSV file.
    If a CSV file is provided, it reads the schema from the CSV.
    If a table_id is provided, it queries the BigQuery INFORMATION_SCHEMA to get the schema.
    The node can contain either a 'csv' key with the path to a CSV file or a 'table_id' key with the format 'project_id.dataset.table'.
    If neither is provided, a NotImplementedError is raised.
    """
    kwargs = loader.construct_mapping(node)
    csv = kwargs.get("csv")
    table_id = kwargs.get("table_id")
    if csv:
        try:
            dataframe = pd.read_csv(csv).fillna(" ")
            parse_schema = lambda row: {
                "column_name": row["fullname"], 
                "data_type": row["type"], 
                "description": row["description"]
            }
            return {
                "schema": [parse_schema(row) for i, row in dataframe.iterrows()]
                }
        except FileNotFoundError:
            pass
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
            "schema": bigquery_job.run(query)
            }
    else:
        raise NotImplementedError("Either csv or table_id must be provided to get or read schema.")

# register the tag handlers
yaml.SafeLoader.add_constructor(tag='!get_env_var', constructor=get_env_var)
yaml.SafeLoader.add_constructor(tag='!concat', constructor=concat)
yaml.SafeLoader.add_constructor(tag='!read_text', constructor=read_text)
yaml.SafeLoader.add_constructor(tag='!read_csv', constructor=read_csv)
yaml.SafeLoader.add_constructor(tag='!read_json', constructor=read_json)
yaml.SafeLoader.add_constructor(tag='!get_or_read_schema', constructor=get_or_read_schema)

with open("resources/config.yml", "r") as f:
    conf:Dict = yaml.safe_load(f)
