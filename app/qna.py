import argparse
from datetime import datetime
from typing import List

from app.main import chatbot
from utils.logging import init_logger


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser(description="Bulk answer queries using the chatbot.")
    parser.add_argument("--relay", type=str, required=True, help="Relay name")
    return parser.parse_args()


def answer(timestamp:str, query:str, get_context:bool=True) -> str:
    """
    Answers a single query using the chatbot.
    """
    bot = chatbot(timestamp, max_react_iterations=20)
    response = bot.answer(query=query, get_context=get_context)
    if "EOS" not in response:
        raise ValueError("Chat did not end with EOS!")
    return response["EOS"]

if __name__ == "__main__":
    args = parse_args()
    relay = f"Answer the question for the relay '{args.relay}'. "
    print(relay)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    init_logger(timestamp)
    with open("resources/qna/queries.txt", "r") as f:
        queries = [line.strip() for line in f if line.strip()]
    results = []
    for query in queries:
        result = answer(timestamp, relay + query)
        results.append(result)
    results = "\n\n".join(results)
    print("Findings:\n\n", results)
    query = "Summarize the following findings into actionable insights:\n\n"
    query += results
    result = answer(timestamp, query, get_context=False)
    print("----------------------------------------------------------------------------------------------------")
    print(result)

# nohup env PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd /home/jupyter/sao-chat python -m app.qna --relay "6751dac12ec73a3ec0dae35c/6752db5f2aa0af75c143bd84/Baseline Scenario" > outputs/qna_expanded_Jun30.out 2>&1 &
