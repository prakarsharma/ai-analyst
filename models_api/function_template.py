
get_available_datasets = {
    "name": "get_available_datasets",
    "description": "Get a list of all available datasets.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    }
}

get_data_dictionary = {
    "name": "get_data_dictionary",
    "description": "Get the data dictionary for a particular dataset using its table ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string", 
                "description": "name of the dataset whose data dictionary is required. Note that this argument should be the name of one of the available datasets returned by the 'get_available_datasets' function."
            }
        },
        "required": [
            "name"
        ],
    }
}

run_bigquery_job = {
    "name": "run_bigquery_job",
    "description": "Accepts a SQL query and submits it to BigQuery to returns a data frame with the results.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "a SQL query to submit to Bigquery. Note that this argument should be a SQL query written in Google SQL syntax."
            }
        },
        "required": [
            "query"
        ],
    }
}

display_results = {
    "name": "display_results",
    "description": "Display the final answer to the user. Note that this function should only be called after you have generated the final answer.",
    "parameters": {
        "type": "object",
        "properties": {
            "results": {
                "type": "string",
                "description": "answer to the user's question."
            }
        },
        "required": [
            "results"
        ],
    }
}