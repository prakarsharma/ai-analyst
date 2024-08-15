import os
import re
import pandas as pd
from unmarkd import unmark
from typing import List, Dict


class clean:
    def __init__(self, string):
        self.string = clean.strip(clean.ravel(string))
        
    def strip(string:str) -> str:
        return string.strip().strip("\n").strip()

    def ravel(string:str) -> str:
        return re.sub("[\\n\\t\\r ]+", " ", string)

    def xml_extract_sql(string:str) -> str:
        try:
            return re.findall("<sql>(.*?)</sql>", string)[-1]
        except IndexError as err:
            raise ValueError("!SQL parsing error!")


class BigQueryJob:
    def __init__(self, safe_mode:bool=False):
        self.safe_mode = safe_mode
        self.platform = os.environ["PLATFORM"]
        self.create_runner()

    def create_runner(self):
        if self.platform == "vertexai":
            self.runner = create_vertexai_bigquery_client(gcloud_project_id=os.environ["GCLOUD_PROJECT_ID"])
        if self.platform == "element":
            self.runner = create_element_bigquery_connection(bigquery_connection=os.environ["BIGQUERY_CONNECTION"])

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


def create_vertexai_bigquery_client(gcloud_project_id:str):
    from google.cloud import bigquery
    def runner(query:str) -> List[Dict[str,str]]:
        dataframe = bigquery.Client(project=gcloud_project_id).query(clean(query).string).result().to_dataframe()
        json = dataframe.astype(str).to_dict(orient="records")
        return json        
    return runner

def create_element_bigquery_connection(bigquery_connection):
    from mlutils import dataset
    def runner(query:str) -> List[Dict[str,str]]:
        dataframe = dataset.load(name=bigquery_connection, query=clean(query).string)
        json = dataframe.astype(str).to_dict(orient="records")
        return json
    return runner

bigquery_job = BigQueryJob()
