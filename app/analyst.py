from typing import Dict, List, Optional, Callable

from utils.config import conf


operations = ["equals", "greater_than", "less_than", "greater_than_or_equals", "less_than_or_equals", "not_equal"]
operators = ["=", ">", "<", ">=", "<=", "!="]
operator_dictionary = {operation:operator for operation, operator in zip(operations,operators)}

class Metrics:
    def number_of(categorical:str, **kwargs) -> str:
        return f"COUNT(DISTINCT {categorical}) AS {categorical}s"

    def average_markdown_percent(**kwargs) -> str:
        return "SUM(current_price - markdown_recommended_price)/SUM(current_price) AS average_markdown_percent"

    def min_markdown_percent(**kwargs) -> str:
        return "MIN((current_price - markdown_recommended_price)/current_price) AS min_markdown_percent"

    def man_markdown_percent(**kwargs) -> str:
        return "MAX((current_price - markdown_recommended_price)/current_price) AS max_markdown_percent"

    def average_sell_through_rate(**kwargs) -> str:
        return "SUM(sales_post_md)/SUM(proj_inv_at_gate) AS average_sell_through_rate"

    def average_sell_through_rate(**kwargs) -> str:
        return "SUM(sales_post_md)/SUM(proj_inv_at_gate) AS average_sell_through_rate"

    def min_sell_through_rate(**kwargs) -> str:
        return "MIN(sales_post_md/ proj_inv_at_gate) AS min_sell_through_rate"

    def max_sell_through_rate(**kwargs) -> str:
        return "MAX(sales_post_md/ proj_inv_at_gate) AS max_sell_through_rate"

    def average_sell_through_rate_without_markdown(**kwargs) -> str:
        return "SUM(str_wo_mkdn * proj_inv_at_gate)/ SUM(proj_inv_at_gate) AS average_sell_through_rate_without_markdown"

    def average_recovery_rate(**kwargs) -> str:
        return "SUM(gmv)/SUM(irv) AS average_recovery_rate"

    def weighted_average_markdown_percent(**kwargs) -> str:
        return "SUM(wt_mkdn_pct)/SUM(proj_inv_at_gate) AS weighted_average_markdown_percent"

    def markdown_percent_percentile(percentile:int, **kwargs) -> str:
        return f"APPROX_QUANTILES(mkdn_pct, 100)[OFFSET({percentile})] AS p{percentile}_markdown_percent"

    def sell_through_rate_percentile(percentile:int, **kwargs) -> str:
        return f"APPROX_QUANTILES(str, 100)[OFFSET({percentile})] AS p{percentile}_sell_through_rate"

    def distribution(categorical:str, **kwargs) -> str:
        return f"COUNT(DISTINCT {categorical})/ (SUM(COUNT(DISTINCT {categorical})) OVER()) AS {categorical}_distribution"

    def total_starting_inventory(**kwargs) -> str:
        return "SUM(proj_inv_at_gate) AS total_starting_inventory"

    def total_budget(**kwargs) -> str:
        return "SUM((current_price - markdown_recommended_price) * proj_inv_at_gate) AS total_budget"

    def total_markdown_sales(**kwargs) -> str:
        return "SUM(sales_post_md) AS total_markdown_sales"

    def total_GMV(**kwargs) -> str:
        return "SUM(sales_post_md * markdown_recommended_price) AS total_GMV"

    def total_starting_inventory_change(**kwargs) -> str:
        return "SUM(proj_inv_at_gate - prev_proj_inv) AS total_starting_inventory_change"

    def total_budget_change(**kwargs) -> str:
        return "SUM((current_price - markdown_recommended_price) * proj_inv_at_gate - (prev_original_price - prev_recommended_price) * prev_proj_inv) AS total_budget_change"

    def total_markdown_sales_change(**kwargs) -> str:
        return "SUM(sales_post_md - prev_post_md_sales) AS total_markdown_sales_change"

    def total_GMV_change(**kwargs) -> str:
        return "SUM(sales_post_md * markdown_recommended_price - prev_post_md_sales * prev_recommended_price) AS total_GMV_change"

    def select(categorical:str, **kwargs) -> str:
        return categorical


class SQL_generator:
    def __init__(self, data_analysis_manifest:Dict):
        self.manifest = data_analysis_manifest
        specifications = self.manifest["args"]["components"]
        self.select_statement = SQL_generator.from_specification("calculations", specifications, SQL_generator.select_expression, sep=", ")
        self.where_clause = SQL_generator.from_specification("filters", specifications, SQL_generator.where_expression, sep=" AND ")
        self.group_by_clause = SQL_generator.from_specification("group_by", specifications, SQL_generator.group_expression, sep=", ")
        self.having_clause = SQL_generator.from_specification("filter_grouped", specifications, SQL_generator.where_expression, sep=" AND ")
        self.order_by_clause = SQL_generator.from_specification("order_by", specifications, SQL_generator.order_expression, sep=", ")

    def select_expression(specification:Dict[str,str]) -> str:
        kwargs = specification.copy()
        metric = kwargs.pop("metric")
        return getattr(Metrics, metric).__call__(**kwargs)

    def where_expression(specification:Dict[str,str]) -> str:
        return f"{specification['data']} {operator_dictionary[specification['conditional_operator']]} {specification['values'][0]}"

    def group_expression(specification:str) -> str:
        return specification

    def order_expression(specification:Dict[str,str]) -> str:
        return f"{specification['data']} {specification.get('ordering', '')}"

    def from_specification(name:str, 
                           specifications:Dict[str,List], 
                           expression:Callable[[],str], 
                           sep:str) -> str:
        clause = []
        spec_list:List = specifications.get(name, [])
        if spec_list:
            try:
                for spec in spec_list:
                    clause.append(expression(spec))
                return sep.join(clause)
            except (KeyError, AttributeError) as err:
                if isinstance(err, KeyError):
                    raise ValueError(f"!incorrect {name} specification!")
                if isinstance(err, AttributeError):
                    raise ValueError(f"!undefined metric {spec['metric']}!")

    def generate(self) -> str:
        if self.select_statement:
            query = f" {self.select_statement} FROM {conf['bigquery']['table']} "
            if self.where_clause:
                query += f" WHERE {self.where_clause} "
            if self.group_by_clause:
                query = f"{self.group_by_clause}," + query
                query += f" GROUP BY {self.group_by_clause} "
                if self.having_clause:
                    query += f" HAVING {self.having_clause} "
            if self.order_by_clause:
                query += f" ORDER BY {self.order_by_clause} "
            return f"SELECT {query}"
        else:
            raise ValueError("!nothing to output!")
