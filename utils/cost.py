from utils.database import query

running_prompt_cost = query("SELECT SUM(count) * 0.5/ 1000000 AS dollar_cost FROM usage_metadata WHERE token_counter = 'promptTokenCount';")[0][0]
running_response_cost = query("SELECT SUM(count) * 1.5/ 1000000 AS dollar_cost FROM usage_metadata WHERE token_counter = 'candidatesTokenCount';")[0][0]
running_cost = running_prompt_cost + running_response_cost