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
    upsert_parent_nodes(examples_db)
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

def upsert_parent_nodes(examples_db):
    document_parts = """
    PREFIX : <file:///examples/>
    SELECT ?node ?part ?document WHERE {
        ?node :part+/:query_string ?document .
        ?part :query_string ?document
    }
    """
    _id_ = ""
    examples = {_id_: {"": {}}}
    for node in examples_graph.query(document_parts):
        items = node.asdict()
        id_ = items.get("node").removeprefix("file:///examples/")
        part = items.get("part").removeprefix("file:///examples/")
        doc = items.get("document").value
        if id_ != _id_:
            examples[_id_].pop("")
            _id_ = id_
            _part_ = ""
            examples[_id_] = {_part_: {"": 0}}
        if part != _part_:
            _part = _part_
            _part_ = part
            examples[_id_][_part_] = {}
            embdngs = examples_db.get(metadata=_part_)
            embdngs = {_doc_:_embdng_ for _doc_, _embdng_ in zip(embdngs["documents"], embdngs["embeddings"])}
        embdng = embdngs[doc]
        for _doc, _embdng in examples[_id_][_part].items():
            examples[_id_][_part_].update({f"{_doc} {doc}": np.array(_embdng) + np.array(embdng)})
    examples.pop("")
    for id_, items in examples.items():
        docs = list(list(items.values())[-1].keys())
        embdngs = [embdng.tolist() for embdng in list(list(items.values())[-1].values())]
        examples_db.upsert(docs, embdngs, metadata=id_)

def get_relevant_examples(prompt:str, examples_db:vectorDB, top_n:Optional[int]=None, **metadata) -> Dict[str, List[str]]:
    paths = {}
    documents = []
    if prompt:
        matches = examples_db.top_matches(prompt, top_n, **metadata)
        documents = examples_db.get(ids=matches["index"])["documents"]
        for node in matches["node"]:
            supporting_documents = """
            BASE <file:///examples/>
            PREFIX : <file:///examples/>
            SELECT ?child ?reference ?recipe WHERE """ +\
            "{" +\
            f"""
            <{node}> :reference*/:name ?reference .
            ?child :name ?reference .
            ?child :recipe ?recipe .""" +\
            "}"
            for child in examples_graph.query(supporting_documents):
                items = child.asdict()
                node = items["child"].removeprefix("file:///examples/")
                reference = items["reference"].value
                recipe = items["recipe"].value
                if node not in paths:
                    hints = """
                    BASE <file:///examples/>
                    PREFIX : <file:///examples/>
                    SELECT ?hint WHERE {
                    OPTIONAL {""" +\
                    f"<{node}> :hint/:recipe ?hint" +\
                    """}
                    }"""
                    hints = [res.asdict().get("hint").value for res in examples_graph.query(hints)]
                    path = {
                        node: {
                            reference: recipe
                        }
                    }
                    if hints:
                        path[node].update({"hints": hints})
                    paths.update(path)
    rules = """
    BASE <file:///examples/>
    PREFIX : <file:///examples/>
    SELECT ?rule WHERE {
    :rule :recipe ?rule
    }
    """
    rules = [rule.asdict()["rule"].value for rule in examples_graph.query(rules)]
    return {
        "examples": documents, 
        "reference": list(paths.values()), 
        "rules": rules
    }
