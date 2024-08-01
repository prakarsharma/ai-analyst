import yaml
import pandas as pd
from typing import Dict


def concat(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(_) for _ in seq])

def read_text(loader, node):
    path = loader.construct_scalar(node)
    with open(path, "r") as f:
        text = f.read()
    return text

def read_schema(loader, node):
    path = loader.construct_scalar(node)
    dataframe = pd.read_csv(path)
    return [{"column_name":row["fullname"],"data_type":row["type"], "description":row["description"]} for i, row in dataframe.iterrows()]

# register the tag handlers
yaml.SafeLoader.add_constructor(tag='!concat', constructor=concat)
yaml.SafeLoader.add_constructor(tag='!read_text', constructor=read_text)
yaml.SafeLoader.add_constructor(tag='!read_schema', constructor=read_schema)

with open("resources/config.yml", "r") as f:
    conf:Dict = yaml.safe_load(f)
