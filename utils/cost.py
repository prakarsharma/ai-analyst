from typing import Literal

from utils.database import query
from utils.config import conf


pricing = {
    "gemini-1.5-pro-001": {
        "input": {
            "rate": 3.5 * 1e-6,
            "limit": 128000,
            "unlimited_rate": 7 * 1e-6
        },
        "output": {
            "rate": 10.5 * 1e-6,
            "limit": 128000,
            "unlimited_rate": 21 * 1e-6
        }
    },
    "gemini-1.0-pro": {
        "input": {
            "rate": 0.5 * 1e-6
        },
        "output": {
            "rate": 1.5 * 1e-6
        }
    }
}

def get_price(price:Literal["input","output"]):
    model:str = conf["models"]["llm"]["name"]
    rate = pricing[model][price]["rate"]
    limit = pricing[model][price].get("limit", 0)
    unlimited_rate = pricing[model][price].get("unlimited_rate", 0)
    count = f"CASE WHEN count <= {limit} THEN count ELSE count * {unlimited_rate/ rate} END" if limit else "count"
    counters = {
        "input": "promptTokenCount", 
        "output": "candidatesTokenCount"
    }
    counter = counters[price]
    query = f"""
SELECT
    SUM({count}) * {rate} AS cost_dollars
FROM
    requested_tokens
WHERE
    token_counter = '{counter}'
    AND model = '{model}';
"""
    return query

running_prompt_cost = query(get_price("input"))[0][0]
running_response_cost = query(get_price("output"))[0][0]

running_cost = f"${running_prompt_cost + running_response_cost}"
