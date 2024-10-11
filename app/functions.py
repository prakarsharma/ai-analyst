import pandas as pd
from matplotlib import pyplot as plt
from io import BytesIO
from typing import List, Dict, Optional
from functools import lru_cache

from app.knowledge import get_relevant_examples
from utils.config import conf
from utils.utils import bigquery_job


def fetch_data(table_id:str, query:str, **kwargs) -> List[Dict[str,str]]:
    """
    Fetch data from BigQuery table and/ or find or compute the different relevant metrics.
    
    Returns
    -------
    dict
        Records returned from query.
    """
    metadata = conf["bigquery"]["combined"]
    if table_id != metadata["table_id"]:
        return {
            "error": f"'{table_id}' is not the correct table ID. Call 'get_markdown_table' to get the correct table ID."
        }
    return bigquery_job.run(query)

@lru_cache
def get_markdown_table(sbu:str="combined", **kwargs) -> Dict:
    """
    Get markdown table ID and related metadata.
    
    Returns
    -------
    dict
        Markdown data table ID, data description, table schema and primary keys.
    """
    metadata = conf["bigquery"].get(sbu.lower())
    return metadata

@lru_cache
def get_dept_sbu_mapping(sbu:Optional[str]=None, 
                         dept:Optional[int]=None, 
                         mapping_table:str=pd.read_csv("resources/combined/dept_SBU_mapping.csv"), **kwargs) -> List[Dict]:
    """
    Get the department name and number from SBU name or department name and SBU name from department number.
    
    Returns
    -------
    dict
        A list of department names and numbers or SBU names.
    """
    SBUs = mapping_table["SBU"].unique()
    Departments = mapping_table["Dept_nbr"].astype(str).unique()
    if sbu:
        if sbu.upper() not in SBUs:
            return {
                "error": f"sbu not found in the list of valid SBU names: {','.join(SBUs)}"
            }
        mapping = mapping_table.loc[mapping_table["SBU"] == sbu.upper(),["Dept_nbr","Dept_desc"]]
    elif dept:
        if str(dept) not in Departments:
            return {
                "error": f"dept not found in the list of valid dept numbers: {','.join(Departments)}"
            }        
        mapping = mapping_table.loc[mapping_table["Dept_nbr"] == dept,["Dept_desc","SBU"]]
    else:
        return {
                "error": "neither sbu or dept was provided. Provide one of them to get mapping."
            }
    return mapping.to_dict(orient="records")

def table(query:str, records:List[Dict]) -> pd.DataFrame:
    """
    Make a table from the records returned by a BigQuery job. This function uses a pandas DataFrame as the choice of tabular data structure.
    
    Returns
    -------
    DataFrame
        A data frame of the queried records.
    """
    return pd.DataFrame(records)

def plot(title:str, x:List, xlabel:str, y:Optional[List]=None, ylabel:str="", plot_type:str="scatter", figsize:List[int]=[8,5]):
    """
    Make a plot (chart) from data provided. This function saves a plot image and does not return anything.
    
    Returns
    -------
        None
    """
    buf = BytesIO()
    df = pd.Series(x, name=xlabel).to_frame()
    fig = plt.figure(figsize=figsize)
    plt.suptitle(title)
    plt.xlabel(xlabel)
    if y is not None:
        y_series = pd.Series(y).astype(float)
        if ylabel:
            df[ylabel] = y_series
            plt.ylabel(ylabel)
    df.sort_values(by=xlabel, ascending=True, inplace=True)
    try:
        if plot_type == "line":
            plt.plot(df[xlabel], df[ylabel])
        if plot_type == "scatter":
            plt.scatter(df[xlabel], df[ylabel])
        if plot_type == "bar":
            plt.bar(df[xlabel], df[ylabel])
        if plot_type == "boxplot":
            plt.boxplot(df[xlabel])
        if plot_type == "histogram":
            plt.hist(df[xlabel])
        if plot_type == "pie":
            plt.pie(df[xlabel])
        fig.savefig(buf, format="png")
        return buf
    except KeyError as err:
        return {
            "error": "provide both x and y to make the plot: either one of the axes is missing or can't be computed"
        }
