import argparse
from datetime import datetime

from app.knowledge import ContextStore
from utils.logging import init_logger


def parse_cli_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Load vector store.")
    parser.add_argument("--overwrite", action="store_true", default=False, help="Overwrite existing vector store (default: False)")
    parser.add_argument("--delete", action="store_true", default=False, help="Delete existing vector store (default: False)")
    args = parser.parse_args()
    return args

def load_vector_store(overwrite:bool=True):
    """
    Load vector store.
    """
    context_store = ContextStore(overwrite=overwrite)
    context_store.load_documents()

def delete_vector_store() -> None:
    """
    Delete the vector store.
    """
    context_store = ContextStore()
    context_store.db.delete()


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    init_logger(timestamp)
    args = parse_cli_args()
    if args.delete:
        delete_vector_store()
    else:
        load_vector_store(args.overwrite)

# PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd /home/jupyter/sao-chat python -m app.load_vector_store