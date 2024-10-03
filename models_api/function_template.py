from app import functions

tools = [
    {
        "name": functions.fetch_data.__name__,
        "description": functions.fetch_data.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "table_id": {
                    "type": "string", 
                    "description": "table ID of the markdown table. You can get it using 'get_markdown_table' function."
                },
                "query": {
                    "type": "string",
                    "description": """a SQL query. Note that the query should be in Google SQL syntax. Do not quote the column names. If the query does not contain all the primary key columns make sure it deduplicates records. The result should always be aggregated. It could be grouped by appropriate column(s). If the query doesn't deduplicate or aggregate it can return millions of records - limit the number of records returned in this case. Follow the same rules on deduplication and aggregation with or without group-by for any sub-queries. Avoid zero-division error in calculation. Sort results by suitable columns and use appropriate aliases where applicable. Use only the provided recipe for calculations."""
                }
            },
            "required": [
                "table_id",
                "query"
            ],
        }
    },

    {
        "name": functions.get_markdown_table.__name__,
        "description": functions.get_markdown_table.__doc__,
        "parameters": {
            "type": "object", 
            "properties": {},
            "required": [],
        }
    },

    {
        "name": functions.get_dept_sbu_mapping.__name__,
        "description": functions.get_dept_sbu_mapping.__doc__,
        "parameters": {
            "type": "object", 
            "properties": {
                "sbu": {
                    "type": "string", 
                    "description": "name of SBU correpsonding to which department names or numbers are required."
                },
                "dept": {
                    "type": "integer", 
                    "description": "Department number corresponding to which a SBU name is required."
                },
            },
            "required": [],
        }
    }
]
