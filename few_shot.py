
table = 'clearance_markdown_ml_prod.vm_final_recommendations_pd'

example = {}

example[0] = dict(
question="Plan no. 3800009. What is the avg markdown percent for the items in department 34?",
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
sql=f"""SELECT AVG(mkdn_pct) AS average_markdown_percent FROM {table} WHERE plan_id = 3800009 AND dept = 34 AND created_timestamp = (SELECT MAX(created_timestamp) FROM {table} WHERE plan_id = 3800009);"""
)