import pandas as pd
import re
from unmarkd import unmark
from mlutils import dataset

from utils.config import conf


examples = pd.read_csv(conf["few_shot"]["examples"]).to_dict(orient="records")


def read_metadata(resource) -> str:
    return ',\n'.join([f"{_[0]} : {_[1]}" for i,_ in pd.read_csv(resource, header=None).iterrows()])

schema = read_metadata(conf["metadata"]["schema"])
metrics = read_metadata(conf["metadata"]["metrics"])
reasons = read_metadata(conf["metadata"]["reasons"])


class clean:
    def __init__(self, string):
        self.string = clean.strip(clean.xml_extract_sql(clean.strip(string)))
        
    def strip(string:str) -> str:
        return string.strip().strip("\n").strip()

    def xml_extract_sql(string:str) -> str:
        try:
            return re.findall("<sql>(.*?)</sql>", string)[-1]
        except IndexError as err:
            raise ValueError("!SQL parsing error!")

class bigquery_connect:
    def __init__(self):
        self.connector:str = conf["bigquery"]["connector"]
        self.table:str = conf["bigquery"]["table"]
        self.test()

    def test(self):
        dataset.load(name=self.connector, query=f"SELECT * FROM {self.table} LIMIT 1;") # one-time connection setting to reduce transactional latency

    def run(self, query:str, is_sql:bool=True) -> pd.DataFrame:
        if is_sql:
            try:
                result = dataset.load(name=self.connector, query=query)
                return result
            except Exception as err:
                raise ConnectionError("!bigquery job failure!")
        return query
