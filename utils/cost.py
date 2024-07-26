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
    model = conf["llm"]["name"]
    rate:float = pricing[conf["llm"]["name"]]["input"]["rate"]
    limit:int = pricing[conf["llm"]["name"]]["input"].get("limit", 0)
    unlimited_rate:float = pricing[conf["llm"]["name"]]["input"].get("unlimited_rate", 0)
    count = "count"
    if limit:
        count = f"CASE WHEN count <= {limit} THEN count ELSE count * {unlimited_rate/ rate} END"
    if price == "input":
        counter = "promptTokenCount"
    if price == "output":
        counter = "candidatesTokenCount"
    query = f"""
SELECT
    SUM({count}) * {rate} AS dollar_cost
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
