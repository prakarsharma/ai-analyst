from app import functions

tools = [
    {
        "name": functions.get_mapping.__name__,
        "description": functions.get_mapping.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "table_id": {
                    "type": "string", 
                    "description": "table ID of the mapping table. You can get it using 'get_mapping_table' function."
                },
                "query": {
                    "type": "string", 
                    "description": "a SQL query to fetch details from the mapping table. If the query does not contain all the primary key columns make sure it deduplicates records."
                }
            },
            "required": [
                "table_id",
                "query"
            ],
        }
    },

    {
        "name": functions.get_mapping_table.__name__,
        "description": functions.get_mapping_table.__doc__,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        }
    },

    {
        "name": functions.fetch_data.__name__,
        "description": functions.fetch_data.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "sbu": {
                    "type": "string",
                    "description": "name of the SBU for which data has to be fetched. You can get it from the mapping table using 'get_mapping' function."
                },
                "table_id": {
                    "type": "string", 
                    "description": "table ID of the SBU data table. You can get it using 'get_sbu_table' function."
                },
                "query": {
                    "type": "string",
                    "description": """a SQL query. Note that the query should be in Google SQL syntax. If the query does not contain all the primary key columns make sure it deduplicates records. The result should always be aggregated and may or may not be grouped by appropriate column(s). Do not group by numeric columns. Avoid zero-division error in calculation. Sort results by suitable columns and use appropriate aliases where applicable."""
                }
            },
            "required": [
                "sbu",
                "table_id",
                "query"
            ],
        }
    },

    {
        "name": functions.get_sbu_table.__name__, 
        "description": functions.get_sbu_table.__doc__, 
        "parameters": {
            "type": "object", 
            "properties": {
                "sbu": {
                    "type": "string", 
                    "description": "name of the SBU for which data has to be fetched. You can get it from the mapping table using 'get_mapping' function."
                }
            }, 
            "required": [
                "sbu"
            ],
        }
    }
]
