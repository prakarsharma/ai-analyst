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
                    "description": """
SQL query. Note that the query should be in Google SQL syntax.
General rules to generate the correct SQL:
Do not quote the column names. Quote only the string and date literals in the query. Do not escape using back-slashes the quotation marks.
Sort results by suitable columns and ensure these columns also appear in the select statement.
Use appropriate aliases where applicable.

Certain data, called metrics, are not available in a table. Metrics have to be computed using the data in the table and simple mathematical operations. Certain metrics may only be defined at a level of aggregation. It depends on the grain of data, i.e., the primary keys. E.g., a metric like, 'duration of sale in days' can only be calculated upon aggrgation if the data is daily. Metrics can be aggregated like other data in the table. An exception to this rule is metrics which are a ratio of two datum. E.g., 'revenue' is a metric defined as 'units times price' - the average revenue is average of revenue - but 'percentage units sold', defined as 'units sold by stock' - the average percentage units sold is sum of units sold by sum of stock. This called the ratio of averages rule.

Rules for calculations to generate the correct SQL:
Aggregate depending on the grain of data.
Deduplicate any string or date type columns in the select statement if there is no aggregation.
Follow the rule of ratio of averages if a metric is a ratio.
Round to 2 decimal places if the expected result is float type.
Avoid zero-division error.
Use only the provided definitions.
"""
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
]
