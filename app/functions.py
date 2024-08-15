import pandas as pd
from typing import List, Dict
from functools import lru_cache

from app.metrics import find_relevant_metrics
from utils.config import conf
from utils.utils import bigquery_job


def get_mapping(query:str, **kwargs) -> List[Dict[str,str]]:
    """
    Fetch data from mapping table.

    Returns
    -------
    dict
        Records returned from a mapping table query.
    """
    results = {"mapping": bigquery_job.run(query)}
    for record in results["mapping"]:
        if "sbu" in record:
            results["sbu"] = record["sbu"]
            metadata = conf["bigquery"][results["sbu"].lower()]
            results.update(metadata)
            relevant_metrics = find_relevant_metrics(kwargs.get("user_prompt"))
            results.update(relevant_metrics)
            break
    return results

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

def fetch_data(sbu:str, query:str, **kwargs) -> List[Dict[str,str]]:
    """
    Fetch data from BigQuery table and/ or find or compute the different relevant metrics. Data for only one SBU can be considered at one time.
    
    Returns
    -------
    dict
        Records returned from SBU data table query.
    """
    return bigquery_job.run(query)
