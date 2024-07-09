metrics = ["number_of", "average_markdown_percent", "min_markdown_percent", "max_markdown_percent", "average_sell_through_rate", "min_sell_through_rate", "max_sell_through_rate", "average_sell_through_rate_without_markdown", "average_recovery_rate", "weighted_average_markdown_percent", "markdown_percent_percentile", "sell_through_rate_percentile", "distribution", "total_starting_inventory", "total_budget", "total_markdown_sales", "total_GMV", "total_starting_inventory_change", "total_budget_change", "total_markdown_sales_change", "total_GMV_change", "select"]

categorical = ["plan_id", "prime_item", "store", "SIC", "dept", "gate_nbr", "target_str", "status", "week_year", "month_year", "markdown_reason", "target_sell_through_rate"]

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
                                    "enum": metrics, 
                                    "description": "name of the metric the user wants to calculate"
                                }, 
                                "percentile": {
                                    "type": "integer", 
                                    "description": "which percentile to calculate when expected output metric is markdown_percent_percentile or sell_through_rate_percentile"
                                }, 
                                "categorical": {
                                    "type": "string", 
                                    "enum": categorical, 
                                    "description": "the data whose count of distinct values to calculate when the expected output metric is number_of, distribution or select"
                                }
                            }, 
                            "required": [
                                "metric"
                            ]
                        }
                    }, 
                    "filters": {
                        "type": "array", 
                        "description": "a list of filters the user wants to apply to the calculation.", 
                        "items": {
                            "description": "specification of a filter the user wants to apply to the calculation", 
                            "type": "object", 
                            "properties": {
                                "data": {
                                    "type": "string", 
                                    "enum": categorical + ["latest_created_timestamp"], 
                                    "description": "the data on which the user wants to apply a filter"
                                }, 
                                "conditional_operator": {
                                    "type": "string", 
                                    "enum": ["equals", "greater_than", "less_than", "greater_than_or_equals", "less_than_or_equals", "not_equal"], 
                                    "description": "the type of conditional operator"
                                }, 
                                "values": {
                                    "type": "array", 
                                    "description": "a list of values on which to filter specified data using the specified conditional operator", 
                                    "items": {
                                        "description": "a value on which to filter specified data. If the value is alphanumeric or date-like use quote it in single quotes. Do not quote if it is stricly numeric.", 
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
                        "description": "List of data by which the user wants to group the calculations", 
                        "items": {
                            "description": "data by which the user wants to group the outputs", 
                            "type": "string", 
                            "enum": categorical
                        }
                    }, 
                    "filter_grouped": {
                        "type": "array", 
                        "description": "a list of filters the user wants to apply on grouped data, i.e., after grouping the calculation", 
                        "items": {
                            "description": "specification of a filter the user wants to apply on grouped data and calculations", 
                            "type": "object", 
                            "properties": {
                                "data": {
                                    "type": "string", 
                                    "enum": metrics, 
                                    "description": "the metric on which the user wants to apply a filter"
                                }, 
                                "conditional_operator": {
                                    "type": "string", 
                                    "enum": ["equals", "greater_than", "less_than", "greater_than_or_equals", "less_than_or_equals", "not_equal"], 
                                    "description": "the type of conditional operator"
                                }, 
                                "values": {
                                    "type": "array", 
                                    "description": "a list of values on which to filter specified data using the specified conditional operator", 
                                    "items": {
                                        "description": "a value on which to filter specified data", 
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
                    "order_by": {
                        "type": "array", 
                        "description": "List of data (or calculations) by which the user wants to arrange the results. List of data (or calculations) which the user wants to see the lowest of or the highest of.", 
                        "items": {
                            "description": "a pair (data, ordering) by which the user want to order the results", 
                            "type": "object", 
                            "properties": {
                                "data": {
                                    "type": "string", 
                                    "enum": categorical, 
                                    "description": "data/ calculation by which the user wants to order the results or wants to see the lowest/ highest of"
                                }, 
                                "ordering": {
                                    "type": "string", 
                                    "enum": ["ascending", "descending"], 
                                    "description": "the ordering by specified data. Whether the specified data should be shown lowest-first or highest-first in the results."
                                }
                            }, 
                            "required": [
                                "data"
                            ]
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
