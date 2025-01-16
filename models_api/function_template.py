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
                    "description": "table ID of the bigquery table. You can get it using 'get_bigquery_table' function."
                },
                "query": {
                    "type": "string",
                    "description": """a SQL query. Note that the query should be in Google SQL syntax. Do not quote the column names. Quote only the string and date literals in the query but do not escape the quotation marks using back-slashes. Take into account the primary-key columns of the table. Aggregate or deduplicate columns as necessary. Avoid zero-division error in calculation. Sort results by suitable columns. Ensure these columns also appear in the select statement. Use appropriate aliases where applicable. Use only the provided recipe for calculations."""
                }
            },
            "required": [
                "table_id",
                "query"
            ],
        }
    },

    {
        "name": functions.get_bigquery_table.__name__,
        "description": functions.get_bigquery_table.__doc__,
        "parameters": {
            "type": "object", 
            "properties": {},
            "required": [],
        }
    },

    # {
        # "name": functions.get_dept_sbu_mapping.__name__,
        # "description": functions.get_dept_sbu_mapping.__doc__,
        # "parameters": {
            # "type": "object", 
            # "properties": {
                # "sbu": {
                    # "type": "string", 
                    # "description": "name of SBU correpsonding to which department names or numbers are required."
                # },
                # "dept": {
                    # "type": "integer", 
                    # "description": "Department number corresponding to which a department name or SBU name is required."
                # },
            # },
            # "required": [],
        # }
    # },

    {
        "name": functions.plot.__name__,
        "description": functions.plot.__doc__,
        "parameters": {
            "type": "object", 
            "properties": {
                "title": {
                    "type": "string", 
                    "description": "a suitable title for the plot."
                },
                "x": {
                    "type": "array", 
                    "description": "a list of data to plot on the x axis.", 
                    "items": {
                        "description": "a value to show on the x axis.", 
                        "type": "string"
                    }
                },
                "xlabel": {
                    "type": "string", 
                    "description": "a suitable name for the data on x axis."
                },
                "y": {
                    "type": "array", 
                    "description": "a list of data to plot on the y axis.", 
                    "items": {
                        "description": "a value to show on the y axis.", 
                        "type": "number"
                    }
                }, 
                "ylabel": {
                    "type": "string", 
                    "description": "a suitable name for the data on y axis."
                },
                "plot_type": {
                    "type": "string", 
                    "enum": ["line", "scatter", "bar", "boxplot", "histogram", "pie"], 
                    "description": "the type of plot."
                }
            },
            "required": [
                "title", 
                "x", 
                "xlabel", 
                "plot_type"
            ],
        }
    },

    # {
        # "name": functions.scratch_pad.__name__,
        # "description": functions.scratch_pad.__doc__,
        # "parameters": {
            # "type": "object", 
            # "properties": {
                # "thoughts": {
                    # "type": "string", 
                    # "description": "Your plan to answer the users question."
                # }
            # },
            # "required": [
                # "thoughts"
            # ],
        # }
    # },

    # {
        # "name": functions.get_more_context.__name__,
        # "description": functions.get_more_context.__doc__,
        # "parameters": {
            # "type": "object", 
            # "properties": {
                # "follow_up_questions": {
                    # "type": "array", 
                    # "description": """A list of questions posed in order to extract more context on the user's query. They are clarifying or knowledge-seeking questions. If the user's query is a multi-part query break it down into simpler single-part questions. Ask about the concepts in the user's query you don't know or cannot assume from your knowledge. Ask as many as possible before assuming anything first.""",
                    # "items": {
                        # "description": """A follow-up question, e.g., given a user query, 'Which stores have a significant YoY growth and met their MSL target?', you can ask questions like 'How is YoY growth calculated?', 'How is MSL target defined?', etc.""",
                        # "type": "string"
                    # },
                    # "minItems": "1",
                    # "maxItems": "3"
                # }
            # },
            # "required": [
                # "follow_up_questions"
            # ],
        # }
    # }
# ]
