
import pandas as pd

examples = [_.to_dict() for i,_ in pd.read_csv('CoT_few_shot_examples.csv').iterrows()]

def prompt_template(question, plan_id, data, column_names, where, where_clause, group_by, outputs, calculations, statement, sql):
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

created_timestamp = (SELECT MAX(created_timestamp) FROM clearance_markdown_ml_prod.vm_final_recommendations_pd WHERE plan_id = {plan_id})

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
    few_shot_prompt = "\n\n".join([prompt_template(**_) for _ in examples])
    system_prompt += f"""Follow the examples provided below enclosed in triple backticks and answer in the same step-by-step format:
```
{few_shot_prompt}
```
"""
    return system_prompt

def generate_prompt(prompt):
    return f"""Question: {prompt}
Let's think step by step,
Answer:
"""