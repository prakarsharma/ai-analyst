import pandas as pd
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
    Get the department name and number from SBU name or SBU name from department number.
    
    Returns
    _______
    dict
        A list of department names and numbers or SBU names.
    """
    SBUs = ["APPAREL", "ENTERTAINMENT TOYS AND SEASONAL", "HARDLINES", "HOME", "FOOD", "CONSUMABLES", "HEALTH AND WELLNESS"]
    Departments = [str(i + 1) for i in range(99) if i + 1 != 68]
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
        mapping = mapping_table.loc[mapping_table["Dept_nbr"] == dept,["SBU"]]
    else:
        return {
                "error": "neither sbu or dept was provided. Provide one of them to get mapping."
            }
    return mapping.to_dict(orient="records")