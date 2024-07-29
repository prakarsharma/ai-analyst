from utils.config import conf

get_plan_dept_sbu_mapping = {
    "name": "get_plan_dept_sbu_mapping",
    "description": "Get the department and/ or Super Business Unit (SBU) for a plan ID or just the SBU for a department.",
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string", 
                "description": "a plan ID. Can be used to fetch either the department or SBU or both."
            },
            "dept_nbr": {
                "type": "string", 
                "description": "a department number. Can be used to fetch the SBU."
            }
        },
        "required": [],
    }    
}

fetch_data = {
    "name": "fetch_data",
    "description": "Accepts a SQL query and submits it to BigQuery to fetch data.",
    "parameters": {
        "type": "object",
        "properties": {
            "sbu": {
                "type": "string",
                "description": "the SBU database from where data has to be fetched."
            },
            "query": {
                "type": "string",
                "description": "a SQL query. Note that the query should be in Google SQL syntax."
            }
        },
        "required": [
            "sbu",
            "query"
        ],
    }
}
