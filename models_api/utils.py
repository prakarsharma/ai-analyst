from datetime import datetime
from typing import Dict

from utils.database import Database
from utils.config import conf
from utils.logging import logger


def record_usage_metadata(usage_metadata:Dict, table_name:str="cost.requested_tokens"):
    """
    Records the usage metadata of an LLM API call into a local database table.
    :param usage_metadata: A dictionary containing the usage metadata, including promptTokenCount, candidatesTokenCount, and totalTokenCount.
    :param table_name: The name of the database table to store the usage metadata. Defaults to "cost.requested_tokens".
    """
    logger.debug("Persisting LLM API usage metadata to '{}'", table_name)
    db = Database(table_name)
    model = conf["models"]["llm"]["name"]
    timestamp = str(datetime.now())
    records = [
        [
            f"'{model}'", 
            f"'{timestamp}'", 
            f"'{token_counter}'", 
            f"{str(count)}"
        ] for token_counter,count in usage_metadata.items()
    ]
    logger.debug("Inserting records:\n{}", "\n".join([", ".join(record) for record in records]))
    db.records_transaction(records)