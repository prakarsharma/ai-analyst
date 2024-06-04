
table = 'clearance_markdown_ml_prod.vm_final_recommendations_pd'

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

example = []

example += [prompt_template(question="Plan no. 3800009. What is the avg markdown percent for the items in department 34?",
plan_id="""
3800009
""",
data="""
1. plan
2. markdown percent
3. department
""",
column_names="""
1. plan is 'plan_id'
2. markdown percent is 'mkdn_pct'
3. department is 'dept'
""",
where="""
1. plan is 3800009
2. department is 34
""",
where_clause="""
plan_id = 3800009 AND dept = 34
""",
group_by="""
none
""",
outputs="""
1. average markdown percent
""",
calculations="""
1. find the average of markdown percent
""",
statement="""
AVG(mkdn_pct) AS average_markdown_percent
""",
sql=f"""SELECT AVG(mkdn_pct) AS average_markdown_percent FROM {table} WHERE plan_id = 3800009 AND dept = 34 AND created_timestamp = (SELECT MAX(created_timestamp) FROM {table} WHERE plan_id = 3800009);""")]