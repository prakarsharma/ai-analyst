import pandas as pd
from matplotlib import pyplot as plt
from io import BytesIO
from typing import List, Dict, Optional
from functools import lru_cache

from utils.config import conf
from utils.utils import bigquery_job
from app.knowledge import generate_relevant_chunks


reflection = False

def fetch_data(table_id:str, query:str, **kwargs) -> List[Dict[str,str]]:
    """
    Fetch data from BigQuery table and/ or find or compute the different relevant metrics.
    
    Returns
    -------
    dict
        Records returned from query.
    """
    metadata = conf["bigquery"]["explainability"]
    if table_id != metadata["table_id"]:
        return {
            "error": f"'{table_id}' is not the correct table ID. Call 'get_bigquery_table' to get the correct table ID."
        }
    global reflection
    reflection = not reflection
    if reflection:
        return {
            "warning": "Verify if the generated query is correct. Reconsider the primary-key columns of the table and ensure the query aggregated or deduplicates columns appropriately. Make corrections, if any, and call 'fetch_data' again."
        }
    result = bigquery_job.run(query)
    reflection = "error" in result
    return result

@lru_cache
def get_bigquery_table(**kwargs) -> Dict:
    """
    Get the bigquery table ID and related metadata.
    
    Returns
    -------
    dict
        Table ID, data description, table schema and primary keys.
    """
    metadata = conf["bigquery"]["explainability"]
    return metadata

# @lru_cache
# def get_dept_sbu_mapping(sbu:Optional[str]=None, 
                         # dept:Optional[int]=None, 
                         # mapping_table:str=pd.read_csv("resources/combined/dept_SBU_mapping.csv"), **kwargs) -> List[Dict]:
    # """
    # Get the department name and number from SBU name or department name and SBU name from department number.
    
    # Returns
    # -------
    # dict
        # A list of department names and numbers or SBU names.
    # """
    # SBUs = mapping_table["SBU"].unique()
    # Departments = mapping_table["Dept_nbr"].astype(str).unique()
    # if sbu:
        # if sbu.upper() not in SBUs:
            # return {
                # "error": f"sbu not found in the list of valid SBU names: {','.join(SBUs)}"
            # }
        # mapping = mapping_table.loc[mapping_table["SBU"] == sbu.upper(),["Dept_nbr","Dept_desc"]]
    # elif dept:
        # if str(dept) not in Departments:
            # return {
                # "error": f"dept not found in the list of valid dept numbers: {','.join(Departments)}"
            # }        
        # mapping = mapping_table.loc[mapping_table["Dept_nbr"] == dept,["Dept_desc","SBU"]]
    # else:
        # return {
                # "error": "neither sbu or dept was provided. Provide one of them to get mapping."
            # }
    # return mapping.to_dict(orient="records")

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

def scratch_pad(thoughts:str):
    """Use a scratch pad to put down thoughts and plan.
    
    Returns
    -------
        None
    """
    pass

def get_more_context(follow_up_questions:List[str]):
    """Retrieve more context on the user's query from a knowledge base on business processes.
    
    Returns
    -------
    dict
        Retrieved context for each follow-up question organized into chunks of knowledge and ordered.
    """
    return {prompt: generate_relevant_chunks(prompt, max_items=5) for prompt in follow_up_questions}
