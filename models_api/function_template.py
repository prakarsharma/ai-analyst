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
                    "description": """a SQL query. Note that the query should be in Google SQL syntax. If the query does not contain all the primary key columns make sure it deduplicates records. The result should always be aggregated and may or may not be grouped by appropriate column(s). Do not group by numeric columns. Avoid zero-division error in calculation. Sort results by suitable columns and use appropriate aliases where applicable."""
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
    }
]
