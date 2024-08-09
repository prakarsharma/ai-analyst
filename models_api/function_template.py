
get_mapping = {
    "name": "get_mapping",
    "description": "Get the plan ID, department and SBU from the mapping table. Always get the SBU for any plan ID or department.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "a SQL query to fetch details from the mapping table. If the query does not contain all the primary key columns make sure it deduplicates records."
            }
        },
        "required": [
            "query"
        ],
    }
}

get_mapping_table = {
    "name": "get_mapping_table",
    "description": "Get the table ID and schema of the mapping table.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    }    
}

fetch_data = {
    "name": "fetch_data",
    "description": "Fetch data from BigQuery table and/ or find or compute the different relevant metrics. Only one SBU can be considered at one time.",
    "parameters": {
        "type": "object",
        "properties": {
            "sbu": {
                "type": "string",
                "description": "the SBU for which data has to be fetched."
            },
            "query": {
                "type": "string",
                "description": "a SQL query. Note that the query should be in Google SQL syntax. If the query does not contain all the primary key columns make sure it deduplicates records. The result should always be aggregated, with or without grouping by, unless the user's question requires only to list the records."
            }
        },
        "required": [
            "sbu",
            "query"
        ],
    }
}
