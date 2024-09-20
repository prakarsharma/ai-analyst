history = [
    {
        'role': 'user', 
        'parts': {
            'text': "How is average markdown percent defined?\n\n{'reference': [{'markdown (discount)': {'recipe': 'dollar markdown/ markdown prior price', 'suggestions': ['Average is computed as: sum of dollar markdown/ sum of markdown prior price.', 'Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To group by markdown: discretize markdown into fixed width bins of width 10% and an upper limit of 100%. Negative or zero, Nulls and > 100% each are separate bins. Group by the bins.', 'To find percentile use SQL APPROX_QUANTILES function.']}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}]}"
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'text': 'Average markdown percent is computed as: sum of dollar markdown/ sum of markdown prior price. \n'
        }
    }, 
    {
        'role': 'user', 
        'parts': {
            'text': "what is the average markdown percent for plan 3964740?\n\n{'reference': [{'markdown (discount)': {'recipe': 'dollar markdown/ markdown prior price', 'suggestions': ['Average is computed as: sum of dollar markdown/ sum of markdown prior price.', 'Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To group by markdown: discretize markdown into fixed width bins of width 10% and an upper limit of 100%. Negative or zero, Nulls and > 100% each are separate bins. Group by the bins.', 'To find percentile use SQL APPROX_QUANTILES function.']}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}]}"
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'functionCall': {
                'name': 'get_markdown_table', 'args': {}
            }
        }
    }, 
    {
        'role': 'function', 
        'parts': {
            'functionResponse': {
                'name': 'get_markdown_table', 
                'response': {
                    'name': 'get_markdown_table', 
                    'content': {
                        'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations', 
                        'description': 'This table contains data on optimzation plan runs. Each plan represents a group of stores and items.', 
                        'schema': {
                            'schema': [
                                {
                                    'column_name': 'dept', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Department number. A double digit integer. It refers to a department.'
                                }, 
                                {
                                    'column_name': 'cat', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Category number'
                                }, 
                                {
                                    'column_name': 'store', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Store number'
                                }, 
                                {
                                    'column_name': 'fineline', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Fineline number'
                                }, 
                                {
                                    'column_name': 'prime_item', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Item number'
                                }, 
                                {
                                    'column_name': 'item', 
                                    'data_type': 'INTEGER', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'ho_rcmd_rtl', 
                                    'data_type': 'NUMERIC', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'base_unit_rtl_amt', 
                                    'data_type': 'NUMERIC', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'effective_date', 
                                    'data_type': 'DATE', 
                                    'description': 'Gate date or review date. The date markdown is applied.'
                                }, 
                                {
                                    'column_name': 'gate_nbr', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Gate number. There are upto 2 gates - 1 and 2. Gate 2 starts after gate 1 ends.'
                                }, 
                                {
                                    'column_name': 'publishing_date', 
                                    'data_type': 'DATE', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'opcode', 
                                    'data_type': 'INTEGER', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'on_hands', 
                                    'data_type': 'INTEGER', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'projected_inv', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Projected starting inventory at gate date'
                                }, 
                                {
                                    'column_name': 'avg_sales_unit_qty', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Average daily sales quantity (units)'
                                }, 
                                {
                                    'column_name': 'daily_sale_wo_markdown', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Average daily sales quantity (units) without markdown (at markdown prior price)'
                                }, 
                                {
                                    'column_name': 'prev_gate_date', 
                                    'data_type': 'DATE', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'prev_gate_rtl', 
                                    'data_type': 'NUMERIC', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'msg_created_ts', 
                                    'data_type': 'TIMESTAMP', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'transaction_id', 
                                    'data_type': 'STRING', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'cmd_cat_nbr', 
                                    'data_type': 'INTEGER', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'retail', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Recommended markdown price'
                                }, 
                                {
                                    'column_name': 'group_original_price', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Group price. Used in the constraints in optimization.'
                                }, 
                                {
                                    'column_name': 'item_original_price', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Markdown prior price'
                                }, 
                                {
                                    'column_name': 'sold_unit', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Estimated sales quantity (units) for the gate duration'
                                }, 
                                {
                                    'column_name': 'selected_elasticity', 
                                    'data_type': 'NUMERIC', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'selected_daily_sale', 
                                    'data_type': 'STRING', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'str_achieved', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Sell Through Rate (STR) expected with markdown. The STR achieved by mathematical optimization.'
                                }, 
                                {
                                    'column_name': 'str_wo_markdown', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Expected Sell Through Rate (STR) without markdown'
                                }, 
                                {
                                    'column_name': 'str_max_feasible', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Expected Sell Through Rate (STR) with max feasible markdown'
                                }, 
                                {
                                    'column_name': 'min_price_point', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Minimum feasible price based on min discount percentage, min discount dollar amount and rounding rules.'
                                }, 
                                {
                                    'column_name': 'max_price_point', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Maximum feasible price based on max discount percentage, max discount dollar amount and rounding rules.'
                                }, 
                                {
                                    'column_name': 'target_str', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Sell Through Rate (STR) target for the optimizer.'
                                }, 
                                {
                                    'column_name': 'upstream_inv', 
                                    'data_type': 'NUMERIC', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'projected_upstream_inv', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Projected upstream inventory (inventory not already accounted) at gate date'
                                }, 
                                {
                                    'column_name': 'upstream_inv_sold', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Estimated sale from upstream inventory'
                                }, 
                                {
                                    'column_name': 'price_grouping_type', 
                                    'data_type': 'STRING', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'price_grouping_id', 
                                    'data_type': 'INTEGER', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'budget', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Budget value input by the user used as a constraint in optimization.  It is unique for a plan run.'
                                }, 
                                {
                                    'column_name': 'max_discount_percentage', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Max discount percentage value input by the user used as a constraint in optimization. It is unique for a plan run.'
                                }, 
                                {
                                    'column_name': 'min_discount_percentage', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Min discount percentage value input by the user used as a constraint in optimization. It is unique for a plan run.'
                                }, 
                                {
                                    'column_name': 'min_discount_absolute', 
                                    'data_type': 'NUMERIC', 
                                    'description': 'Absolute min discount value input by the user used as a constraint in optimization. It is unique for a plan run.'
                                }, 
                                {
                                    'column_name': 'markdown_reason', 
                                    'data_type': 'STRING', 
                                    'description': "Remarks on markown pricing optimization. A code which represents a particular optimization result or markdown pricing reason. Valid codes are:\n'OPTIMIZER_STR_ACHIEVED': optimal discount solution satisfies target STR requirement and achieves the highest gate sales it could.\n'LOW_PRICE': Group price meets the low price criteria. Applied the low price rule directly without optimization.\n'OPTIMIZER_STR_NOT_ACHIEVED_STORE_INVENTORY': optimal discount solution DOES NOT satisfy target STR requirement due to the remaining store inventory.\n'OPTIMIZER_STR_NOT_ACHIEVED_UPSTREAM_INVENTORY': optimal discount solution DOES NOT satisfy target STR requirement due to the remaining upstream inventory.\n'INFEASIBLE_DEFAULT_MARKDOWN': infeasible optimization. No feasible markdown price lies within min and max bounds. Applied default markdown.\n'BUDGET_INFEASIBLE_MIN_MARKDOWN': infeasible optimization. The plan does not stay witihn the budget required. Applied min markdown.\n'MISSING_ELASTICITY_MIN_MARKDOWN': missing elasticity. Applied min markdown.\n'ZERO_OR_MISSING_AVG_DAILY_SALE_MIN_MARKDOWN': zero or missing average daily sales data. Applied min markdown.\n'ZERO_OR_MISSING_PROJECTED_INVENTORY_MIN_MARKDOWN': zero or missing projected start inventory at gate\n'MARKDOWN_NOT_NEEDED': markdown is not mandatory. Target STR achieved without any markdown."
                                }, 
                                {
                                    'column_name': 'error_msg', 
                                    'data_type': 'STRING', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'model_id', 
                                    'data_type': 'INTEGER', 
                                    'description': ' '
                                }, 
                                {
                                    'column_name': 'create_timestamp', 
                                    'data_type': 'TIMESTAMP', 
                                    'description': "Plan run creation timestamp in 'yyyy-mm-dd HH:MM:SS' UTC format"
                                }, 
                                {
                                    'column_name': 'cmd_plan_id', 
                                    'data_type': 'INTEGER', 
                                    'description': 'Plan ID as sent by CMD team. A 7 digit integer. It refers to an optimization plan.'
                                }
                            ]
                        }, 
                        'primary_key': ['plan_id', 'store', 'prime_item', 'gate_nbr', 'created_timestamp']
                    }
                }
            }
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'functionCall': {
                'name': 'fetch_data', 
                'args': {
                    'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations', 
                    'query': 'SELECT SUM(item_original_price - retail)/SUM(item_original_price) FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 3964740'
                }
            }
        }
    }, 
    {
        'role': 'function', 
        'parts': {
            'functionResponse': {
                'name': 'fetch_data', 
                'response': {
                    'name': 'fetch_data', 
                    'content': [
                        {
                            'f0_': '0.372957516'
                        }
                    ]
                }
            }
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'text': 'The average markdown percent for plan 3964740 is 37.3%. \n'
        }
    }, 
    # {
        # 'role': 'user', 
        # 'parts': {
            # 'text': "Can you tell me the wt avg markdown and 90th percentile markdown by gate for the plan 3964740?\n\n{'reference': [{'markdown (discount)': {'recipe': 'dollar markdown/ markdown prior price', 'suggestions': ['Average is computed as: sum of dollar markdown/ sum of markdown prior price.', 'Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To group by markdown: discretize markdown into fixed width bins of width 10% and an upper limit of 100%. Negative or zero, Nulls and > 100% each are separate bins. Group by the bins.', 'To find percentile use SQL APPROX_QUANTILES function.']}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}, {'markdown spend': {'recipe': 'dollar markdown * starting inventory', 'suggestions': []}}]}"
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'functionCall': {
                # 'name': 'fetch_data', 
                # 'args': {
                    # 'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations', 
                    # 'query': 'SELECT gate_nbr, SUM((item_original_price - retail) * (projected_inv + projected_upstream_inv))/SUM(projected_inv + projected_upstream_inv) AS wt_avg_markdown, APPROX_QUANTILES((item_original_price - retail)/item_original_price, 100)[OFFSET(90)] AS percentile_90_markdown FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 3964740 GROUP BY gate_nbr'
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'function', 
        # 'parts': {
            # 'functionResponse': {
                # 'name': 'fetch_data', 
                # 'response': {
                    # 'name': 'fetch_data', 
                    # 'content': [
                        # {
                            # 'gate_nbr': '2', 
                            # 'wt_avg_markdown': '1.734062117', 
                            # 'percentile_90_markdown': '0.375000000'
                        # }, 
                        # {
                            # 'gate_nbr': '1', 
                            # 'wt_avg_markdown': '2.470000000', 
                            # 'percentile_90_markdown': '0.552572707'
                        # }
                    # ]
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'text': 'The wt avg markdown and 90th percentile markdown for plan 3964740 are as follows:\nGate 1 - wt avg markdown: 2.47, 90th percentile markdown: 55.26%\nGate 2 - wt avg markdown: 1.73, 90th percentile markdown: 37.5% \n\n'
        # }
    # }, 
    # {
        # 'role': 'user', 
        # 'parts': {
            # 'text': "How is average STR defined?\n\n{'reference': [{'Sell Through Rate (STR)': {'recipe': 'sales quantity (units)/ starting inventory', 'suggestions': ['Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To find percentile use SQL APPROX_QUANTILES function.']}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}]}"
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'text': 'Average STR is computed as: sum of column weighted with starting inventory/ sum of starting inventory. \n\n'
        # }
    # }, 
    # {
        # 'role': 'user', 
        # 'parts': {
            # 'text': "what is the str achieved by gate for the plan 3964740?\n\n{'reference': [{'Sell Through Rate (STR)': {'recipe': 'sales quantity (units)/ starting inventory', 'suggestions': ['Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To find percentile use SQL APPROX_QUANTILES function.']}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}]}"
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'functionCall': {
                # 'name': 'fetch_data', 
                # 'args': {
                    # 'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations', 
                    # 'query': 'SELECT gate_nbr, SUM(str_achieved * (projected_inv + projected_upstream_inv))/SUM(projected_inv + projected_upstream_inv) AS avg_str FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 3964740 GROUP BY gate_nbr'
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'function', 
        # 'parts': {
            # 'functionResponse': {
                # 'name': 'fetch_data', 
                # 'response': {
                    # 'name': 'fetch_data', 
                    # 'content': [
                        # {
                            # 'gate_nbr': '2', 
                            # 'avg_str': 
                            # '0.521148345'
                        # }, 
                        # {
                            # 'gate_nbr': '1', 
                            # 'avg_str': '0.500000000'
                        # }
                    # ]
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'text': 'The average STR achieved for plan 3964740 are as follows:\nGate 1 - 50.0%\nGate 2 - 52.11% \n'
        # }
    # }, 
    # {
        # 'role': 'user', 
        # 'parts': {
            # 'text': "What is the number of store-Items combinations which have markdown percent greater than 60% and inventory less than 1 for plan 3964740.\n\n{'reference': [{'store-item combination (SIC)': {'recipe': 'Concatenate store number and item number.', 'suggestions': ['Use SQL CONCAT function.']}}]}"
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'functionCall': {
                # 'name': 'fetch_data', 
                # 'args': {
                    # 'query': 'SELECT COUNT(DISTINCT CONCAT(CAST(store as STRING), CAST(prime_item as STRING))) FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 3964740 AND (item_original_price - retail)/item_original_price > 0.6 AND (projected_inv + projected_upstream_inv) < 1', 
                    # 'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations'
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'function', 
        # 'parts': {
            # 'functionResponse': {
                # 'name': 'fetch_data', 
                # 'response': {
                    # 'name': 'fetch_data', 
                    # 'content': [
                        # {
                            # 'f0_': '0'
                        # }
                    # ]
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'text': 'There are 0 store-item combinations with markdown percent greater than 60% and inventory less than 1 for plan 3964740. \n'
        # }
    # }, 
    # {
        # 'role': 'user', 
        # 'parts': {
            # 'text': "Give me summary statistics for plan 4000011 by gate.\n\n{'reference': [{'store-item combination (SIC)': {'recipe': 'Concatenate store number and item number.', 'suggestions': ['Use SQL CONCAT function.']}}]}"
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'functionCall': {
                # 'name': 'fetch_data', 
                # 'args': {
                    # 'query': 'SELECT gate_nbr, SUM(item_original_price - retail)/SUM(item_original_price) AS avg_markdown_percent, APPROX_QUANTILES((item_original_price - retail)/item_original_price, 100)[OFFSET(90)] AS percentile_90_markdown, SUM((item_original_price - retail)/item_original_price * (projected_inv + projected_upstream_inv))/SUM(projected_inv + projected_upstream_inv) AS wt_avg_markdown, SUM(str_achieved * (projected_inv + projected_upstream_inv))/SUM(projected_inv + projected_upstream_inv) AS avg_str FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 4000011 GROUP BY gate_nbr', 'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations'
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'function', 
        # 'parts': {
            # 'functionResponse': {
                # 'name': 'fetch_data', 
                # 'response': {
                    # 'name': 'fetch_data', 
                    # 'content': [
                        # {
                            # 'gate_nbr': '2', 
                            # 'avg_markdown_percent': '0.378930618', 
                            # 'percentile_90_markdown': '0.571428571', 
                            # 'wt_avg_markdown': '2.407365963', 
                            # 'avg_str': '0.962487846'
                        # }, 
                        # {
                            # 'gate_nbr': '1', 
                            # 'avg_markdown_percent': '0.423435892', 
                            # 'percentile_90_markdown': '0.799599198', 
                            # 'wt_avg_markdown': '10.633055048', 
                            # 'avg_str': '0.679438131'
                        # }
                    # ]
                # }
            # }
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'text': 'The summary statistics for plan 4000011 are as follows:\nGate 1 - average markdown percent: 42.34%, 90th percentile markdown: 79.96%, weighted average markdown: 10.63, and average STR achieved: 67.94%.\nGate 2 - average markdown percent: 37.89%, 90th percentile markdown: 57.14%, weighted average markdown: 2.41, and average STR achieved: 96.25%. \n'
        # }
    # }, 
    # {
        # 'role': 'user', 
        # 'parts': {
            # 'text': "How is markdown spend defined?\n\n{'reference': [{'markdown spend': {'recipe': 'dollar markdown * starting inventory', 'suggestions': ['To find a change in it find the change over time, i.e., change in its value from the previous plan run timestamp. Calculate its value - its value for the previous plan run timestamp .', 'To explain why it has changed: find the change in optimization result by gate and plan run timestamp. Optimization result is the distribution by markdown reason codes.']}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}, {'markdown (discount)': {'recipe': 'dollar markdown/ markdown prior price', 'suggestions': ['Average is computed as: sum of dollar markdown/ sum of markdown prior price.', 'Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To group by markdown: discretize markdown into fixed width bins of width 10% and an upper limit of 100%. Negative or zero, Nulls and > 100% each are separate bins. Group by the bins.', 'To find percentile use SQL APPROX_QUANTILES function.']}}]}"
        # }
    # }, 
    # {
        # 'role': 'model', 
        # 'parts': {
            # 'text': 'Markdown spend is calculated as: (markdown prior price - markdown price) * (projected starting inventory + projected upstream inventory). \n'
        # }
    # }, 
    {
        'role': 'user', 
        'parts': {
            'text': "How much has markdown spend changed for plan 4000011 for each gate over the different timestamps?\n\n{'reference': [{'markdown spend': {'recipe': 'dollar markdown * starting inventory', 'suggestions': ['To find a change in it find the change over time, i.e., change in its value from the previous plan run timestamp. Calculate its value - its value for the previous plan run timestamp .', 'To explain why it has changed: find the change in optimization result by gate and plan run timestamp. Optimization result is the distribution by markdown reason codes.']}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}, {'markdown (discount)': {'recipe': 'dollar markdown/ markdown prior price', 'suggestions': ['Average is computed as: sum of dollar markdown/ sum of markdown prior price.', 'Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To group by markdown: discretize markdown into fixed width bins of width 10% and an upper limit of 100%. Negative or zero, Nulls and > 100% each are separate bins. Group by the bins.', 'To find percentile use SQL APPROX_QUANTILES function.']}}]}"
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'functionCall': {
                'name': 'fetch_data', 
                'args': {
                    'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations', 
                    'query': 'SELECT gate_nbr, create_timestamp, SUM((item_original_price - retail)*(projected_inv + projected_upstream_inv)) AS markdown_spend FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 4000011 GROUP BY gate_nbr, create_timestamp ORDER BY gate_nbr, create_timestamp'
                }
            }
        }
    }, 
    {
        'role': 'function', 
        'parts': {
            'functionResponse': {
                'name': 'fetch_data', 
                'response': {
                    'name': 'fetch_data', 
                    'content': [
                        {
                            'gate_nbr': '1', 
                            'create_timestamp': '2024-08-26 16:35:42.474000+00:00', 
                            'markdown_spend': '16820772.571900000'
                        }, 
                        {
                            'gate_nbr': '1', 
                            'create_timestamp': '2024-08-26 17:18:09.725000+00:00', 
                            'markdown_spend': '13497483.401900000'
                        }, 
                        {
                            'gate_nbr': '1', 
                            'create_timestamp': '2024-08-26 19:18:57.792000+00:00', 
                            'markdown_spend': '16820785.711900000'
                        }, 
                        {
                            'gate_nbr': '1', 
                            'create_timestamp': '2024-08-27 17:23:15.172000+00:00', 
                            'markdown_spend': '13472387.194600000'
                        }, 
                        {
                            'gate_nbr': '2', 
                            'create_timestamp': '2024-08-26 16:35:42.474000+00:00', 
                            'markdown_spend': '761318.495000000'
                        }, 
                        {
                            'gate_nbr': '2', 
                            'create_timestamp': '2024-08-26 17:18:09.725000+00:00', 
                            'markdown_spend': '1515921.890000000'
                        }, 
                        {
                            'gate_nbr': '2', 
                            'create_timestamp': '2024-08-26 19:18:57.792000+00:00', 
                            'markdown_spend': '761209.415000000'
                        }, 
                        {
                            'gate_nbr': '2', 
                            'create_timestamp': '2024-08-27 17:23:15.172000+00:00', 
                            'markdown_spend': '1403115.292500000'
                        }
                    ]
                }
            }
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'text': 'Markdown spend for plan 4000011 changed over different timestamps within each gate as follows:\nGate 1:\n    On 2024-08-26 16:35:42.474000+00:00, it was 16820772.57.\n    On 2024-08-26 17:18:09.725000+00:00, it was 13497483.40.\n    On 2024-08-26 19:18:57.792000+00:00, it was 16820785.71.\n    On 2024-08-27 17:23:15.172000+00:00, it was 13472387.19.\nGate 2:\n    On 2024-08-26 16:35:42.474000+00:00, it was 761318.50.\n    On 2024-08-26 17:18:09.725000+00:00, it was 1515921.89.\n    On 2024-08-26 19:18:57.792000+00:00, it was 761209.42.\n    On 2024-08-27 17:23:15.172000+00:00, it was 1403115.29. \n'
        }
    }, 
    {
        'role': 'user', 
        'parts': {
            'text': "give me 5 recent plans created in the last 1 month\n\n{'reference': []}"
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'functionCall': {
                'name': 'fetch_data', 
                'args': {
                    'query': 'SELECT DISTINCT cmd_plan_id FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE CAST(create_timestamp as DATE) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH) AND CURRENT_DATE() LIMIT 5', 
                    'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations'
                }
            }
        }
    }, 
    {
        'role': 'function', 
        'parts': {
            'functionResponse': {
                'name': 'fetch_data', 
                'response': {
                    'name': 'fetch_data', 
                    'content': [
                        {
                            'cmd_plan_id': '3962309'
                        }, 
                        {
                            'cmd_plan_id': '3944551'
                        }, 
                        {
                            'cmd_plan_id': '4000748'
                        }, 
                        {
                            'cmd_plan_id': '4008747'
                        }, 
                        {
                            'cmd_plan_id': '3939785'
                        }
                    ]
                }
            }
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'text': 'Here are 5 plans created in the last 1 month: 3962309, 3944551, 4000748, 4008747, 3939785. \n'
        }
    },
    {
        'role': 'user', 
        'parts': {
            'text': "What is the budget for plan 4000011?\n\n{'reference': [{'markdown spend': {'recipe': 'dollar markdown * starting inventory', 'suggestions': ['To find a change in it find the change over time, i.e., change in its value from the previous plan run timestamp. Calculate its value - its value for the previous plan run timestamp .', 'To explain why it has changed: find the change in optimization result by gate and plan run timestamp. Optimization result is the distribution by markdown reason codes.']}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}]}"
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'functionCall': {
                'name': 'fetch_data', 
                'args': {
                    'query': 'SELECT DISTINCT budget FROM wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations WHERE cmd_plan_id = 4000011', 
                    'table_id': 'wmt-mtech-assortment-ml-prod.clearance_markdown_ml_prod.final_recommendations'
                }
            }
        }
    }, 
    {
        'role': 'function', 
        'parts': {
            'functionResponse': {
                'name': 'fetch_data', 
                'response': {
                    'name': 'fetch_data', 
                    'content': [
                        {
                            'budget': ''
                        }, 
                        {
                            'budget': '13500000'
                        }, 
                        {
                            'budget': '8700000'
                        }
                    ]
                }
            }
        }
    }, 
    {
        'role': 'model', 
        'parts': {
            'text': 'The budget varies between 8700000 and 13500000. \n'
        }
    },
    # {
    #     'role': 'user', 
    #     'parts': {
    #         'text': "Why has markdown spend changed for the plan 4000011?\n\n{'reference': [{'markdown spend': {'recipe': 'dollar markdown * starting inventory', 'suggestions': []}}, {'dollar markdown (absolute discount)': {'recipe': 'markdown prior price - markdown price', 'suggestions': []}}, {'starting inventory': {'recipe': 'projected starting inventory + projected upstream inventory', 'suggestions': []}}, {'markdown (discount)': {'recipe': 'dollar markdown/ markdown prior price', 'suggestions': ['Average is computed as: sum of dollar markdown/ sum of markdown prior price.', 'Weighted average is computed as: sum of column weighted with starting inventory/ sum of starting inventory', 'To group by markdown: discretize markdown into fixed width bins of width 10% and an upper limit of 100%. Negative or zero, Nulls and > 100% each are separate bins. Group by the bins.', 'To find percentile use SQL APPROX_QUANTILES function.']}}]}"
    #     }
    # }, 
    # {
    #     'role': 'model', 
    #     'parts': {
    #         'text': 'I cannot answer that question. There is no information on what factors impact markdown spend. \n'
    #     }
    # }
]
