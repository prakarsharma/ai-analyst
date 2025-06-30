import argparse
from datetime import datetime
from typing import Dict, Optional

from app.knowledge import RetrievalPipeline
from utils.logging import init_logger


def parse_cli_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Retrieve context based on a query.")
    parser.add_argument("--query", type=str, required=True, help="Query text")
    parser.add_argument("--rephrase_query", action="store_true", default=False, help="Rephrase the query (default: False)")
    parser.add_argument("--top_n", type=int, help="Number of top results to retrieve")
    parser.add_argument("--evaluate", action="store_true", default=False, help="Retrieval results evaluation (default: False)")
    
    args = parser.parse_args()
    return args

def retrieve_context(query:str, 
                     rephrase_query:bool=False, 
                     top_n:Optional[int]=None, 
                     evaluate:bool=False, 
                     **kwargs) -> Dict:
    """
    Retrieve context based on the query.
    """
    retrieval_pipeline = RetrievalPipeline(rephrase_query=rephrase_query, 
                                           top_n=top_n, 
                                           evaluate=evaluate, 
                                           **kwargs)
    results = retrieval_pipeline.retrieve(query)
    return results


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    init_logger(timestamp)
    args = parse_cli_args()
    experiment = f"experiment_{timestamp}"
    results = retrieve_context(args.query, 
                               args.rephrase_query, 
                               args.top_n, 
                               args.evaluate, 
                               experiment=experiment)

# PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd /home/jupyter/sao-chat python -m app.retrieve --query "For the relay '6751dac12ec73a3ec0dae35c/6752db5f2aa0af75c143bd84/Baseline Scenario', was there a PoD growth or decline overall?"