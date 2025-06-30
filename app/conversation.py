from datetime import datetime
from typing import List

from app.main import chatbot
from utils.logging import init_logger

def start_conversation(timestamp:str, queries:List[str]=[]) -> str:
    """
    Create a conversation with the chatbot.
    """
    bot = chatbot(timestamp)
    for query in queries[:-1]:
        response = bot.answer(query=query, get_context=True)
        if "EOS" not in response:
            raise ValueError("Chat did not end with EOS!")
        bot.chat.append("model", response["EOS"])
    response = bot.answer(query=queries[-1], get_context=False)
    if "EOS" not in response:
        raise ValueError("Chat did not end with EOS!")
    return response["EOS"]

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    init_logger(timestamp)
    with open("resources/qna/queries.txt", "r") as f:
        queries = [line.strip() for line in f if line.strip()]
    answer = start_conversation(timestamp, queries) # FAIL: ends in hitting the context window token limit
    print(end="\n")
    print(answer, end="\n")

# nohup env PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd /home/jupyter/sao-chat python -m app.conversation > outputs/conversation.out 2>&1 &
