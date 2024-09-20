import os
import shutil
import numpy as np
from rdflib import Graph
from typing import List, Dict, Optional

from models_api.vectorize import vectorDB
from utils.config import conf

examples_graph = Graph().parse(conf["knowledge"]["documents"]["examples"])

def graph_to_DB():
    shutil.rmtree(conf["knowledge"]["db"]["path"])
    os.makedirs(conf["knowledge"]["db"]["path"])
    examples_db = vectorDB(name="examples")
    upsert_child_nodes(examples_db)
    return f"upserted {examples_db.n_docs} documents"

def upsert_child_nodes(examples_db):
    documents_dump = """
    PREFIX : <file:///examples/>
    SELECT ?node ?query_string WHERE {
        ?node :query_string ?query_string
    }
    """
    documents = {}
    for node in examples_graph.query(documents_dump):
        items = node.asdict()
        id_ = items.get("node").removeprefix("file:///examples/")
        qry_str = items.get("query_string").value
        if id_ not in documents:
            documents[id_] = []
        documents[id_].append(qry_str)
    for id_, docs in documents.items():
        examples_db.upsert(docs, metadata=id_)

def get_relevant_examples(prompt:str, examples_db:vectorDB, top_n:Optional[int]=None, **metadata) -> Dict[str, List[str]]:
    paths = {}
    if prompt:
        matches = examples_db.top_matches(prompt, top_n, **metadata)
        for match in matches["node"]:
            supporting_documents = """
            BASE <file:///examples/>
            PREFIX : <file:///examples/>
            SELECT ?child ?reference ?recipe WHERE """ +\
            "{" +\
            f"""
            <{match}> :reference*/:query_string ?reference .
            ?child :query_string ?reference .
            ?child :recipe ?recipe .""" +\
            "}"
            for child in examples_graph.query(supporting_documents):
                items = child.asdict()
                node = items["child"].removeprefix("file:///examples/")
                reference = items["reference"].value
                recipe = items["recipe"].value
                if node not in paths:
                    suggestions = """
                    BASE <file:///examples/>
                    PREFIX : <file:///examples/>
                    SELECT ?suggestion WHERE {
                    OPTIONAL {""" +\
                    f"<{node}> :suggestion+/:recipe ?suggestion" +\
                    """}
                    }"""
                    suggestions = [res.asdict().get("suggestion").value for res in examples_graph.query(suggestions)]
                    path = {
                        node: {
                            reference: {
                                "recipe": recipe, 
                                "suggestions": suggestions
                            }
                        }
                    }
                    paths.update(path)
    return {"reference": list(paths.values())}
