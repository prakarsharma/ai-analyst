import pandas as pd
from typing import List, Dict
from functools import lru_cache

from app.metrics import find_relevant_metrics
from utils.config import conf
from utils.utils import bigquery_job


def get_mapping(table_id:str, query:str, **kwargs) -> List[Dict[str,str]]:
    """
    Fetch data from mapping table.

    Returns
    -------
    dict
        Records returned from a mapping table query.
    """
    if table_id != conf["bigquery"]["mapping"]["table_id"]:
        return {
            "error": f"'{table_id}' is not the correct table ID for the mapping table. Call 'get_mapping_table' to get the correct table ID."
        }
    return bigquery_job.run(query)

@lru_cache
def get_mapping_table(**kwargs) -> Dict:
    """
    Get mapping table ID and related metadata.

    Returns
    -------
    dict
        Table ID, table data description, table schema and primary keys.
    """
    metadata = conf["bigquery"]["mapping"]
    return metadata

def fetch_data(sbu:str, table_id:str, query:str, **kwargs) -> List[Dict]:
    """
    Fetch data from BigQuery table and/ or find or compute the different relevant metrics. Data for only one SBU can be considered at one time.
    
    Returns
    -------
    dict
        Records returned from SBU data table query.
    """
    metadata = conf["bigquery"].get(sbu.lower())
    if not metadata:
        return {
            "error": f"'{sbu}' is not a valid SBU name. Get valid SBU name from mapping table."
        }
    if table_id != metadata["table_id"]:
        return {
            "error": f"'{table_id}' is not the correct table ID for '{sbu}' data table. Call 'get_sbu_table' to get the correct table ID."
        }
    return bigquery_job.run(query)

@lru_cache
def get_sbu_table(sbu:str, **kwargs) -> Dict:
    """
    Get SBU data table ID and related metadata.
    
    Returns
    -------
    dict
        Table ID, table data description, table schema and primary keys. Along with metadata a set of relevant metrics (w.r.t. the user's question), their definitions and some supporting information is also returned.
    """
    metadata = conf["bigquery"].get(sbu.lower())
    if not metadata:
        return {
            "error": f"'{sbu}' is not a valid SBU name. Get valid SBU name from mapping table."
        }
    metadata.update(find_relevant_metrics(kwargs.get("user_prompt")))
    return metadata
