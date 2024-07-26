import re
import pandas as pd
from unmarkd import unmark
from typing import List, Dict

from utils.config import conf


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


def create_vertexai_bigquery_client():
    from google.cloud import bigquery
    project_id = conf["vertexai"]["project_id"]
    def runner(query:str) -> List[Dict[str,str]]:
        return bigquery.Client(project=project_id).query(clean(query).string).result().to_dataframe().to_dict(orient="records")
    return runner

def create_element_bigquery_connection():
    from mlutils import dataset
    connector = conf["element"]["bigquery"]["connector"]
    def runner(query:str) -> List[Dict[str,str]]:
        return dataset.load(name=connector, query=clean(query).string).to_dict(orient="records")
    return runner
