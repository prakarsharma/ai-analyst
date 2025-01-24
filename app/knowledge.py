import os
import shutil
import json
# import numpy as np
# from rdflib import Graph
from typing import List, Dict, Optional

from models_api.vectorize import vectorDB
from models_api.system_prompt import semantics_expert
from models_api.gemini_api import chat_request, chat_api_message
from models_api.generate import llm
from utils.config import conf


column_descriptions = {field["column_name"].lower(): field["description"]  for field in conf["bigquery"]["explainability"]["schema"]["schema"]}
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


def analyze_and_retrieve_context(prompt:str, attached_files:List[str]=["gs://p0s0a31/sao_chatbot/kg/optimization_limited_v2.txt"]):
    message = chat_api_message()
    prompter = lambda role, user_prompt: f"Find out all the chunks of knowledge relevant to the user's query: {user_prompt}"
    message.append("user", prompt, formatter=prompter, attached_files=attached_files)
    analyzer_retriever_response = {
        "type": "OBJECT",
        "properties": {
            "analysis": {
                "type": "ARRAY",
                "description": "a list of pairs of question and context",
                "items": {
                    "description": "a question along with the context on the question",
                    "type": "OBJECT",
                    "properties": {
                        "question": {
                            "type": "STRING",
                            "description": "a simple clarifying or knowledge-seeking question on the user's query"
                        },
                        "context": {
                            "type": "ARRAY",
                            "description": "a list of knowledge chunks relevant to a question",
                            "items": {
                                "type": "STRING",
                                "description": "the text of the relevant chunk as in the user provided document"
                            },
                        },
                    },
                    "required": [
                        "question", 
                        "context"
                    ]
                },
            }
        },
        "required": [
            "analysis"
        ]
    }
    analyzer_retriever = llm(semantics_expert)
    response_object = analyzer_retriever.request(message.messages, response_schema=analyzer_retriever_response)
    response = chat_request.parse_response(response_object)
    for i, part in enumerate(message.messages[-1]["parts"]):
        if "fileData" in part:
            message.messages[-1]["parts"].pop(i)
    message.append("model", **response)
    message.append("user", "Consider the relevant knowledge found in the previous step. Find all corresponding relevant columns from the attached schema document.", attached_files=["gs://p0s0a31/sao_chatbot/kg/schema_limited.txt"])
    column_name_response = analyzer_retriever_response.copy()
    columns = {
        "columns": {
            "type": "ARRAY",
            "description": "a list of columns relevant to a question and context",
            "items": {
                "type": "STRING",
                "description": "the name of a relevant column as in the user provided schema document"
            },
        }
    }
    column_name_response["properties"]["analysis"]["items"]["properties"].update(columns)
    column_name_response["properties"]["analysis"]["items"]["required"].append("columns")
    response_object = analyzer_retriever.request(message.messages, response_schema=column_name_response)
    response = chat_request.parse_response(response_object)
    return [
        {
            "Follow-up question": field["question"], 
            "Context": field["context"], 
            "Relevant columns": {
                name: column_descriptions[name.lower()] for name in field["columns"]
            }
        } for field in json.loads(response["response"])["analysis"]
    ]
