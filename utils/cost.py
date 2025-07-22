from typing import Literal

from utils.database import Database
from utils.config import conf


pricing = {
    "gemini-2.0-flash-001": {
        "input": {
            "rate": 0.1 * 1e-6
        },
        "output": {
            "rate": 0.4 * 1e-6
        }
    },
    "gemini-1.5-pro-001": {
        "input": {
            "rate": 1.25 * 1e-6,
            "limit": 128000,
            "unlimited_rate": 2.5 * 1e-6
        },
        "output": {
            "rate": 5 * 1e-6,
            "limit": 128000,
            "unlimited_rate": 10 * 1e-6
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

counters = {
    "input": "promptTokenCount", 
    "output": "candidatesTokenCount"
}

def get_price(tokens_type:Literal["input","output"]):
    """
    Formulates a SQL query to calculate the cost of requested tokens for a specific model and token type.
    The tokens_type can be either 'input' or 'output'.
    The function retrieves the model name from the configuration and uses it to look up the pricing details
    in the pricing dictionary.
    It constructs a SQL query that sums the cost of tokens based on the rate and any applicable limits or unlimited rates.
    The query filters the results based on the token type and model.
    The result will be the total cost in dollars for the requested tokens of the specified type and model.
    """
    model:str = conf["models"]["llm"]["name"]
    model_pricing = pricing[model][tokens_type]
    rate = model_pricing["rate"]
    limit = model_pricing.get("limit", 0)
    unlimited_rate = model_pricing.get("unlimited_rate", 0)
    count = f"CASE WHEN count <= {limit} THEN count ELSE count * {unlimited_rate/ rate} END" if limit else "count"
    counter = counters[tokens_type]
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

db = Database("cost.requested_tokens")
running_prompt_cost = db.query(get_price("input"))[0][0]
running_response_cost = db.query(get_price("output"))[0][0]
running_cost = f"${running_prompt_cost + running_response_cost}"