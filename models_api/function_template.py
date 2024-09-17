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
                    "description": """a SQL query. Note that the query should be in Google SQL syntax. Use only the columns names in the schema of the used table. Do not quote the column names. Deduplicate the non-numeric columns in the query to avoid returning too many records. Note that the user requires results in summarized form so aggregate the numeric columns, grouping by appropriate columns. But do not group by numeric columns or calculated expressions. Include the columns used to group by in the results. Use appropriate aliases where applicable. Use only the formulae and hints provided as reference for the calculations and strictly follow all the given rules."""
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
