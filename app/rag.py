import argparse
from datetime import datetime

from models_api.gemini_api import chat_api_message
from app.main import AugmentedGenerationPipeline
from utils.logging import init_logger


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def parse_cli_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate response to a query with specified augmentations.")
    parser.add_argument("--query", type=str, required=True, help="Query text")
    parser.add_argument("--get_context", action="store_true", default=False, help="Retrieve context based on the query to augment response generation (default: True)")
    parser.add_argument("--analyze", action="store_true", default=False, help="Analyze the query before response generation (default: False)")
    parser.add_argument("--plan", action="store_true", default=False, help="Plan the response before generation (default: True)")
    parser.add_argument("--evaluate", action="store_true", default=False, help="Evaluate the generated response (default: False)")
    args = parser.parse_args()
    return args

def retrieve_augment_generate(system_prompt:str, 
                              query:str, 
                              get_context:bool=False, 
                              analyze:bool=False, 
                              plan:bool=False, 
                              evaluate:bool=False) -> str:
    """
    Retrieve context based on the query and generate a response given the additional context using the LLM.
    """
    chat = chat_api_message()
    generation_pipeline = AugmentedGenerationPipeline(system_prompt=system_prompt, 
                                                      evaluate=evaluate, 
                                                      experiment=f"experiment_{timestamp}")
    generation_pipeline.add_retriever(experiment=f"experiment_{timestamp}")
    prompt = generation_pipeline.prompt(query, 
                                        retrieval_augmentation=get_context, 
                                        analysis_augmentation=analyze, 
                                        thought_augmentation=plan)
    chat.append("user", prompt)
    response = generation_pipeline.generate_chat(chat)
    return response["response"]

if __name__ == "__main__":
    init_logger(timestamp)
    args = parse_cli_args()
    system_prompt = "You are a helpful assistant."
    response = retrieve_augment_generate(system_prompt, 
                                         args.query, 
                                         args.get_context, 
                                         args.analyze, 
                                         args.plan, 
                                         args.evaluate)
    print(end="\n")
    print(response, end="\n")

# PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd /home/jupyter/sao-chat python -m app.rag --query "For the relay '674dd6b861ff62ebf309117c/674f87b63a47b26624dca030/50% Protect', was there a PoD growth or decline overall?" --get_context