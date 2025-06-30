import argparse
from datetime import datetime

from app.main import chatbot
from utils.logging import init_logger

def parse_cli_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Chatbot CLI for generating responses.")
    parser.add_argument("--query", type=str, required=True, help="Your query")
    parser.add_argument("--get_context", action="store_true", default=False, help="Retrieve context based on the query to augment response generation (default: False)")
    parser.add_argument("--analyze", action="store_true", default=False, help="Analyze the query before response generation (default: False)")
    parser.add_argument("--plan", action="store_true", default=False, help="Plan the response before generation (default: False)")
    args = parser.parse_args()
    return args

def react(timestamp:str, 
          query:str, 
          get_context:bool=False, 
          analyze:bool=False, 
          plan:bool=False):
    """
    Start a chatbot process.
    """
    bot = chatbot(timestamp)
    response = bot.answer(query=query, 
                          get_context=get_context, 
                          analyze=analyze, 
                          plan=plan)
    return response

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    init_logger(timestamp)
    args = parse_cli_args()
    answer = react(timestamp, 
                   query=args.query, 
                   get_context=args.get_context, 
                   analyze=args.analyze, 
                   plan=args.plan)
    print(end="\n")
    print(answer, end="\n")

# PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd /home/jupyter/sao-chat python -m app.react --query "For the relay '6751dac12ec73a3ec0dae35c/6752db5f2aa0af75c143bd84/Baseline Scenario', was there a PoD growth or decline overall?" --get_context