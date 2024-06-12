
import pandas as pd

schema = ',\n'.join([f"{_['fullname']} : {_['description']}" for i,_ in pd.read_csv("latest_plan_report_table.csv").iterrows()])
metrics = ',\n'.join([f"{_['fullname']} : {_['definition']}" for i,_ in pd.read_csv("metrics.csv").iterrows()])
reasons = ',\n'.join([f"{_['reason']} : {_['Explanation']}" for i,_ in pd.read_csv("markdown_reason_codes.csv").iterrows()])

system_prompt = f"""Consider a table named 'clearance_markdown_ml_prod.vm_fin_rec_pd_lat_pln_rpt'. Use the schema with column names and their meanings provided below in a dictionary format enclosed in angular brackets:
<
{schema}
>
As data analysis expert, your job is to write a SQL query which can return the output the user expects from this table. Use the metrics definitions provided below in a dictionary format enclosed in double angular brackets:
<<
{metrics}
>>
For markdown reason codes refer the dictionary provided below enclosed in triple angular brackets:
<<<
{reasons}
>>>

"""

examples = [_.to_dict() for i,_ in pd.read_csv('CoT_few_shot_examples.csv').iterrows()]

def prompt_template(question, data, column_names, where, where_clause, group_by, outputs, calculations, statement, sql):
    prompt = f"""Question: {question}
Let's think step by step,
Answer: 
step 1: Find what data is required from the table.
{data}
step 2: Fetch corresponding column names from the schema.
{column_names}
step 3: Identify the filter conditions.
{where}
step 4: Write the WHERE clause in GoogleSQL.
{where_clause}
step 5: Identify the columns to group by.
{group_by}
step 6: Find what outputs are required.
{outputs}
step 7: Calculate the outputs.
{calculations}
step 8. Write the SELECT statement in GoogleSQL with aliases.
{statement}
step 9. Return the generated SQL enclosed in sql xml tags:
<sql> {sql} </sql>
"""
    return prompt

def generate_few_shot_prompt(system_prompt=system_prompt):
    few_shot_prompt = "\n\n".join([prompt_template(**_) for _ in examples])
    system_prompt += f"""Follow the examples provided below enclosed in quadruple angular brackets and answer in the same step-by-step format:
<<<<
{few_shot_prompt}
>>>>
"""
    return system_prompt

def generate_prompt(prompt):
    return f"""Question: {prompt}
Let's think step by step,
Answer:
"""