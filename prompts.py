
import pandas as pd
from few_shot import example

def generate_few_shot_prompt(system_prompt):
    examples = "\n\n".join(example)
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