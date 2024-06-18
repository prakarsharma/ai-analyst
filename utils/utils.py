import pandas as pd


def schema(file="resources/latest_plan_report_table.csv") -> str:
    return ',\n'.join([f"{_[0]} : {_[1]}" for i,_ in pd.read_csv(file, header=None).iterrows()])

def clean_text(response:str) -> str:
    return response.strip().strip("\n").strip()