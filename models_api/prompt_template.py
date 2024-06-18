from typing import List, Dict

from utils.utils import schema


system_prompt = f"""
Consider a table named 'clearance_markdown_ml_prod.vm_fin_rec_pd_lat_pln_rpt'. Use the schema with column names and their meanings provided below in a dictionary format enclosed in angular brackets:
<
{schema()}
>
As data analysis expert, your job is to write a SQL query which can return the output the user expects from this table. Don't add any comments in the query. Don't give any explanation of the query. Limit the query to return a maximum of 10 records only. Give meaningful aliases to all the calculated columns in the query. The aliases should be in snake case. Use GoogleSQL syntax in the query.
"""

def streamlit_message(role:str, message:str) -> Dict[str, str]:
        return {"role": role, "content": message}

class gemini_chat_api_message:
    def __init__(self, user_prompt:str=None):
        self._messages = []
        if user_prompt:
            self.append("user", user_prompt)

    def template(role:str, message:str) -> Dict[str, str]:
        return {
            "role": role,
            "parts": {"text": message}
        }

    def append(self, role:str, message:str):
        self._messages.append(gemini_chat_api_message.template(role, message))

    @property
    def messages(self) -> List[Dict]:
        return self._messages
