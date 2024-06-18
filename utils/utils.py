import pandas as pd
import re
from unmarkd import unmark
from mlutils import dataset

from utils.config import conf


def schema(file="resources/latest_plan_report_table.csv") -> str:
    return ',\n'.join([f"{_[0]} : {_[1]}" for i,_ in pd.read_csv(file, header=None).iterrows()])

class clean:
    def strip(string) -> str:
        return string.strip().strip("\n").strip()

    def unmark_sql(string):
        return re.sub("^sql", "", clean.strip(unmark(string).strip("`")))

class bigquery_connect:
    def __init__(self):
        self.connector:str = conf["bigquery"]["connector"]
        self.table:str = conf["bigquery"]["table"]
        self.test()

    def test(self):
        dataset.load(name=self.connector, query=f"SELECT * FROM {self.table} LIMIT 1;") # one-time connection setting to reduce transactional latency

    def run(self, query:str, is_sql:bool=True) -> pd.DataFrame:
        if is_sql:
            return dataset.load(name=self.connector, query=query)
        return query
