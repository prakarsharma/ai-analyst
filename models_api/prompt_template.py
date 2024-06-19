from typing import List, Dict, Callable

from utils.config import conf
from utils.utils import schema, metrics, reasons, examples


system_prompt = f"""
Consider a table named {conf['bigquery']['table']}. Use the schema with column names and their meanings provided below in a dictionary format enclosed in angular brackets:
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


def streamlit_message(role:str, message:str) -> Dict[str, str]:
        return {"role": role, "content": message}


class few_shot:
    def __init__(self, system_prompt:str=system_prompt):
        self.system_prompt = system_prompt
        self.few_shot_examples = few_shot.get_few_shot_examples()
        self.system_prompt += f"""Follow the examples provided below enclosed in quadruple angular brackets and answer in the same step-by-step format:
<<<<
{self.few_shot_examples}
>>>>
"""
    def get_few_shot_examples(examples:List[Dict[str,str]]=examples) -> str:
        return "\n\n".join([few_shot.CoT_prompt(**_) for _ in examples]).format(price_drivers_table=conf["bigquery"]["table"])

    def CoT_prompt(question:str, 
                   data:str, 
                   column_names:str, 
                   where:str, 
                   where_clause:str, 
                   group_by:str, 
                   outputs:str, 
                   calculations:str, 
                   statement:str, 
                   sql:str) -> str:
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

    def format_user_prompt(role:str, prompt:str) -> str:
        if role == "user":
            return f"""Question: {prompt}
Let's think step by step,
Answer:
"""
        return prompt


class gemini_chat_api_message:
    def __init__(self, user_prompt:str=None):
        self._messages = []
        if user_prompt:
            self.append("user", user_prompt)

    def template(role:str, message:str, formatter:Callable[[str,str],str]=few_shot.format_user_prompt) -> Dict[str, str]:
        return {
            "role": role,
            "parts": {"text": formatter(role, message)}
        }

    def append(self, role:str, message:str):
        self._messages.append(gemini_chat_api_message.template(role, message))

    @property
    def messages(self) -> List[Dict]:
        return self._messages
