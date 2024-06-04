
import pandas as pd
from few_shot import table, example

def prompt_template(question, plan_id, data, column_names, where, where_clause, group_by, outputs, calculations, statement, sql, table=table):
    prompt = f"""Question: {question}
Let's think step by step,
Answer: 
step 1: Note the plan no.
{plan_id}
step 2: Find what data is required from the table.
{data}
step 3: Fetch corresponding column names from the data dictionary.
{column_names}
step 4: Identify the filter conditions.
{where}
step 5: Write the WHERE clause in GoogleSQL.
{where_clause}
step 6: Add a condition to the WHERE clause to get the records only for the latest timestamp.

created_timestamp = (SELECT MAX(created_timestamp) FROM {table} WHERE plan_id = {plan_id})

step 7: Identify the columns to group by.
{group_by}
step 8: Find what outputs are required.
{outputs}
step 9: Calculate the outputs.
{calculations}
step 10. Write the SELECT statement in GoogleSQL with aliases.
{statement}
step 11. Return the generated SQL in markdown format (starting with triple backticks immediately followed by 'sql' and ending in triple backticks):
```sql {sql} ```
"""
    return prompt

def generate_few_shot_prompt(system_prompt):
    examples = "\n\n".join([prompt_template(**example_i) for i, example_i in example.items()])
    system_prompt += f"""Follow the examples provided below enclosed in triple backticks and answer in the same step-by-step format:
```
{examples}
```
"""
    return system_prompt

def generate_prompt(prompt):
    return f"""Question: {prompt}
Let's think step by step,
Answer:
"""