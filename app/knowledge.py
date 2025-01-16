import os
import shutil
# import numpy as np
# from rdflib import Graph
from typing import List, Dict, Optional

from models_api.vectorize import vectorDB
from models_api.system_prompt import doc_expert
from models_api.gemini_api import chat_request, chat_api_message
from models_api.generate import llm
from utils.config import conf


kg = conf["knowledge"]["documents"]["graph"]

def load_graph_into_db(name="chunks"):
    shutil.rmtree(conf["knowledge"]["db"]["path"])
    os.makedirs(conf["knowledge"]["db"]["path"])
    chunks_db = vectorDB(name=name)
    upsert_nodes(chunks_db)
    return f"upserted {chunks_db.n_docs} documents"

def upsert_nodes(chunks_db):
    documents = {
        id_: chunk["txt"] for id_, chunk in kg.items()
    }
    chunks_db.upsert(documents)

def get_relevant_chunks(prompt:str, chunks_db:vectorDB, top_n:Optional[int]=None, max_depth:Optional[int]=5, max_breadth:Optional[int]=5, **metadata) -> Dict[str, List[str]]:
    chunks = []
    ids = []
    if prompt:
        matches = chunks_db.top_matches(prompt, top_n, **metadata)
        for i, match in enumerate(matches["node"]):
            if str(match) not in ids:
                node = kg[str(match)]
                ids += [str(match)]
                chunks_ = traverse(node, ids, max_depth=max_depth, max_breadth=max_breadth)
                ids += list(chunks_.keys())
                chunks += [
                    {
                        "no.": i+1, 
                        "relevant": node["txt"], 
                        "supporting": list(chunks_.values())
                    }
                ]
    return {"context": chunks}

def traverse(node:Dict, ids:List, depth:int=1, max_depth:int=5, max_breadth:int=5):
    chunks_ = {}
    related = [str(_) for _ in node["rel"]]
    related = list(set(related) - set(ids))[:max_breadth]
    if depth < max_depth and related:
        for id_ in related:
            node_ = kg[id_]
            chunks_[id_] = node_["txt"]
            ids += [id_]
            chunks_.update(traverse(node_, ids, depth+1, max_depth, max_breadth))
    return chunks_


def generate_relevant_chunks(prompt:str, min_items:int=0, max_items:int=10, attached_files:List[str]=["gs://p0s0a31/sao_chatbot/kg/optimization.txt"]):
    message = chat_api_message()
    prompter = lambda role, user_prompt: f"Find out all the chunks of knowledge relevant to the user's query: {user_prompt}"
    message.append("user", prompt, formatter=prompter, attached_files=attached_files)
    chunk_retriever_response = {
        "type": "OBJECT",
        "properties": {
            "context": {
                "type": "ARRAY",
                "description": "a list of chunks",
                "items": {
                    "description": "a chunk characterized by a rank and text",
                    "type": "OBJECT",
                    "properties": {
                        "no.": {
                            "type": "INTEGER",
                            "description": "rank based on relevance"
                        },
                        "relevant": {
                            "type": "STRING",
                            "description": "the text of a relevant chunk as in the user provided document"
                        },
                        # "supporting": {
                            # "type": "ARRAY",
                            # "description": "a list of chunks which contain any supporting information on the relevant chunk",
                            # "items": {
                                # "type": "STRING",
                                # "description": "the text of a supporting chunk as in the user provided document"
                            # },
                            # "minItems": "0",
                            # "maxItems": "5"
                        # }
                    },
                    "required": [
                        "no.",
                        "relevant",
                        # "supporting"
                    ]
                },
                "minItems": str(min_items),
                "maxItems": str(max_items)
            }
        },
        "required": [
            "context"
        ]
    }
    retriever = llm(doc_expert, response_schema=chunk_retriever_response)
    response_object = retriever.request(message.messages)
    response = chat_request.parse_response(response_object)
    return response["response"]
