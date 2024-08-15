from app import functions
tools = [{
        "name": functions.get_mapping.__name__,
        "description": functions.get_mapping.__doc__,
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
                    "description": "the SBU for which data has to be fetched"
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
]
