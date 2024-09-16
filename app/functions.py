import pandas as pd
from typing import List, Dict
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
