from app.functions import Tools

tools = [
    {
        "name": Tools.submit_query_plan.__name__,
        "description": Tools.submit_query_plan.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "details": {
                    "type": "string", 
                    "description": """Details of the query plan.
                    It should cover the following:
                    1. Sources of data, i.e., the tables.
                    2. The grain of data, i.e., the primary keys for all the tables.
                    3. Join conditions, join type, the join keys and the left and right tables, if a join is necessary.
                    4. Filter conditions, if any.
                    5. Grouping columns, if required, considering the grain of data.
                    6. Filter conditions on grouped data, if needed.
                    7. The metrics to be calculated and their aliases. Mention the summary functions and window functions, if used.
                    8. Ordering of the results, if applicable.
                    9. Any assumptions.
                    10. Any additional information that may be relevant.
                    """
                }
            },
            "required": [
                "details"
            ],
        }
    },
    {
        "name": Tools.fetch_data.__name__,
        "description": Tools.fetch_data.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "table_id": {
                    "type": "array", 
                    "description": """A list of table IDs from which to fetch data. Call 'get_bigquery_table' to get the correct table IDs.""",
                    "items": {
                        "type": "string",
                        "description": "A table ID"
                    },
                },
                "query": {
                    "type": "string",
                    "description": """SQL query. Note that the query should be in Google SQL syntax.
                    General rules to generate the correct SQL:
                    1. Do not use new line characters in the query. The query should be a single line string.
                    2. Do not quote the column names.
                    3. Quote only the string and date literals in the query.
                    4. Do not escape using back-slashes the quotation marks.
                    5. Sort results by suitable columns and ensure these columns also appear in the select statement.
                    6. Use appropriate aliases where applicable.

                    Metrics calculation:
                    Metrics are data which are not directly available in a table. Metrics have to be computed using the data in the table and simple mathematical operations as per their definition.
                    Certain metrics may only be defined at a level of aggregation. It depends on the grain of data, i.e., the primary keys.
                    E.g., a metric like, 'duration of sale in days' can only be calculated upon aggregation if the data is daily.
                    Metrics can be aggregated like other data in the table. An exception to this rule is metrics which are a ratio of two datum.
                    E.g., 'revenue' is a metric defined as 'units times price' - the average revenue is average of revenue - but 'percentage units sold', defined as 'units sold by stock' - the average percentage units sold is sum of units sold by sum of stock. This called the ratio of averages rule.

                    Rules for calculations to generate the correct SQL:
                    1. Aggregate depending on the grain of data.
                    2. Deduplicate any string or date type columns in the select statement if there is no aggregation.
                    3. Follow the rule of ratio of averages if a metric is a ratio.
                    4. Round to 2 decimal places if the expected result is float type.
                    5. Avoid zero-division error.
                    6. Use only the provided metrics definitions."""
                }
            },
            "required": [
                "table_id",
                "query"
            ],
        }
    },

    {
        "name": Tools.get_bigquery_table.__name__,
        "description": Tools.get_bigquery_table.__doc__,
        "parameters": {
            "type": "object", 
            "properties": {},
            "required": [],
        }
    },

    # {
        # "name": Tools.get_dept_sbu_mapping.__name__,
        # "description": Tools.get_dept_sbu_mapping.__doc__,
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
        "name": Tools.plot.__name__,
        "description": Tools.plot.__doc__,
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
        # "name": Tools.scratch_pad.__name__,
        # "description": Tools.scratch_pad.__doc__,
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
        # "name": Tools.get_more_context.__name__,
        # "description": Tools.get_more_context.__doc__,
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
    {
        "name": Tools.EOS.__name__,
        "description": Tools.EOS.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to return to the user."
                }
            },
            "required": [
                "message"
            ],
        }
    }
]