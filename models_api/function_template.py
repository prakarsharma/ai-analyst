
data_analysis_manifest = {
    "name": "data_analysis_manifest", 
    "description": "Given a question, if the user expects a data-based answer, generate a data analysis manifest.", 
    "parameters": {
        "type": "object", 
        "properties": {
            "components": {
                "type": "object", 
                "properties": {
                    "calculations": {
                        "type": "array", 
                        "description": "a list of metrics the user wants to calculate", 
                        "items": {
                            "description": "the metrics user wants to calculate", 
                            "type": "object", 
                            "properties": {
                                "metric": {
                                    "type": "string", 
                                    "enum": ["average_markdown_percent", "average_sell_through_rate", "average_recovery_rate", "weighted_average_markdown_percent", "markdown_percent_percentile", "sell_through_rate_percentile", "count_rows", "count_distinct", "distribution"], 
                                    "description": "name of the metric the user wants to calculate"
                                }, 
                                "percentile": {
                                    "type": "integer", 
                                    "description": "which percentile to calculate when expected output metric is markdown_percent_percentile or sell_through_rate_percentile"
                                }, 
                                "categorical_column": {
                                    "type": "string", 
                                    "enum": ["item_nbr", "store_nbr", "plan_id"], 
                                    "description": "name of the column whose count of distinct values to calculate when the expected output metric is count_distinct"
                                }
                            }, 
                            "required": [
                                "metric"
                            ]
                        }
                    }, 
                    "filters": {
                        "type": "array", 
                        "description": "a list of filters the user wants to apply to the calculation. To apply ", 
                        "items": {
                            "description": "specification of a filter the user wants to apply to the calculation", 
                            "type": "object", 
                            "properties": {
                                "data": {
                                    "type": "string", 
                                    "enum": ["plan_id", "department", "date", "week_year", "month_year", "markdown_reason", "gate"], 
                                    "description": "name of the column on which the user wants to apply a filter"
                                }, 
                                "conditional_operator": {
                                    "type": "string", 
                                    "enum": ["equals", "greater_than", "less_than", "greater_than_or_equals", "less_than_or_equals", "not_equal"], 
                                    "description": "the type of conditional operator"
                                }, 
                                "values": {
                                    "type": "array", 
                                    "description": "a list of values on which the user wants to filter the specified data using the specified conditional operator", 
                                    "items": {
                                        "description": "a value on which the user wants to filter the specified data", 
                                        "type": "string"
                                    }
                                }
                            }, 
                            "required": [
                                "data", 
                                "conditional_operator", 
                                "values"
                            ]
                        }
                    }, 
                    "group_by": {
                        "type": "array", 
                        "description": "List of all features by which the user wants to group the calculations", 
                        "items": {
                            "description": "name of the column by which to group the outputs", 
                            "type": "string", 
                            "enum": ["gate", "target_sell_through_rate", "markdown_reason", "plan_id", "item_nbr", "store_nbr"]
                        }
                    }
                },
                "required": [
                    "calculations",
                    "filters"
                ]
            }
        }
    }
}
