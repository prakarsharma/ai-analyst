import os
import re
from typing import List, Dict, Optional, Literal, cast

from models_api.vectorize import vectorDB
from models_api.system_prompt import semantics_expert
from models_api.generate import llm
from app.eval import llmJudge
from utils.config import conf
from utils.logging import logger
from utils.utils import read_gcs_file, chmod_R


class ContextStore:
    """
    This class stores documment chunks along with additional context for each chunk.
    It provides methods to chunk documents, annotate chunks with additional context and retrieve relevant chunks based on a query.
    It uses a vector database for storage and an LLM for generating context.
    """
    def __init__(self, 
                 path:str=conf["vector_database"]["path"], 
                 document_uris:List[str]=conf["vector_database"]["document_uris"], 
                 chunk_size:str=conf["vector_database"]["chunk_size"], 
                 chunk_overlap:int=conf["vector_database"]["chunk_overlap"], 
                 annotate_chunks:bool=conf["vector_database"]["annotate_chunks"], 
                 **kwargs):
        """
        Initializes the ContextStore with a vector database and an LLM annotator.
        :param path: The path to the vector database.
        :param document_uris: A list of URIs pointing to the documents to be processed.
        :param chunk_size: The size of the document chunks (default: "sentence").
        :param chunk_overlap: The overlap size between document chunks (default: 0).
        :param annotate_chunks: Whether to annotate chunks with additional context (default: False).
        """
        logger.info("Initializing ContextStore")
        self.path = path
        logger.info("Attaching documents")
        self.document_uris = document_uris
        logger.info("Loading chunking configuration")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.annotate_chunks = annotate_chunks
        if self.annotate_chunks:
            logger.info("Initializing an LLM for semantic analyses")
            self.expert = llm(semantics_expert)
        logger.info("Initializing vector database")
        self.name = f"{self.chunk_size}s_{'overlapping-' + str(self.chunk_overlap) if self.chunk_overlap else 'non-overlapping'}_{'annotated' if self.annotate_chunks else 'raw'}"
        self.db = vectorDB(self.name, self.path, **kwargs)


    @property
    def n_docs(self) -> int:
        return self.db.n_docs

    def chunk_document(self, document:str) -> List[str]:
        """
        This method chunks a document into smaller pieces based on the specified chunk size and overlap.
        :param document: The document to be chunked.
        :return: A list of document chunks.
        """
        if self.chunk_size == "sentence":
            logger.info("Chunking document into sentences")
            sentences = re.split(r'(?<=[.!?])\s+', document) # Split document into sentences at sentence boundaries - periods, question marks, or exclamation marks followed by a space or newline
            chunks = [_.strip() for _ in sentences if _.strip()] # Filter out empty sentences
            logger.info("Chunked document into {} sentences", len(chunks))
        if self.chunk_overlap > 0:
            logger.info("Overlapping chunks with overlap size: {}", self.chunk_overlap)
            overlapped_chunks = []
            for i in range(len(chunks)):
                start_i = max(0, i - self.chunk_overlap)
                end_i = min(len(chunks), i + self.chunk_overlap)
                overlapping_chunks = " ".join(chunks[start_i:end_i])
                overlapped_chunks.append(overlapping_chunks)
            chunks = overlapped_chunks
            logger.info("Created {} overlapping chunks", len(chunks))
        return chunks

    def annotate(self, chunks:List[str]) -> List[Dict]:
        """
        This method annotates each chunk with helpful additional context from user provided documents.
        It uses an LLM to generate annotations for each chunk.
        :param chunks: A list of document chunks to be annotated.
        :return: A list of dictionaries, each containing a chunk, its context, and keywords.
        """
        logger.info("Annotating chunks")
        annotator = lambda role, chunk: f"""
        With reference to the attached document, here is the chunk we want to situate within the whole document:
        <chunk> 
        {chunk}
        </chunk> 
        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
        """
        annotation_response_schema = {
            "type": "OBJECT",
            "properties": {
                "context": {
                    "type": "STRING",
                    "description": "A short succinct context that situates the chunk within the overall document."
                },
                "keywords": {
                    "type": "ARRAY",
                    "description": "A list of keywords mentioned in the chunk.",
                    "items": {
                        "type": "STRING",
                        "description": "A keyword from the chunk."
                    }
                }
            },
            "required": [
                "context", 
                "keywords"
            ]
        }
        annotated_chunks = []
        for chunk in chunks:
            annotations = self.expert.generate(
                chunk, 
                formatter=annotator, 
                attached_files=self.document_uris, 
                response_schema=annotation_response_schema
            )
            annotations = cast(dict, annotations)
            annotated_chunks.append(
                {
                "chunk": chunk,
                "context": annotations["context"],
                "keywords": annotations["keywords"]
                }
            )
            logger.debug("Annotated chunk: {}", "\n" + annotated_chunks[-1]["chunk"])
            context = annotated_chunks[-1].get("context", "no additional context provided")
            keywords = ", ".join(annotated_chunks[-1].get("keywords", [])) or "no keywords found"
            logger.debug("Context: {}", context)
            logger.debug("Keywords: {}", keywords)
        logger.info("Annotated {} chunks with context", len(annotated_chunks))
        return annotated_chunks

    def chunk(self) -> List[str]:
        """
        This method reads documents from the specified URIs and chunks them into smaller pieces.
        It can annotate each chunk, if specified.
        :return: A list of document chunks with annotations, if any.
        """
        chunks = []
        for uri in self.document_uris:
            logger.info("Chunking document: {}", uri)
            document = read_gcs_file(uri)
            chunks.extend(self.chunk_document(document))
        if self.annotate_chunks:
            annotated_chunks = self.annotate(chunks)
            chunks = []
            for annotation in annotated_chunks:
                chunks.append(f"""{annotation["chunk"]}\n{annotation["context"]}""")
        else:
            logger.info("Skipping annotation")
        return chunks

    def store(self, document_chunks:List[str]):
        """
        This method stores document chunks in a vector database.
        :param document_chunks: A list containing document chunks.
        """
        logger.info("Storing chunks")
        documents = {str(i): chunk for i, chunk in enumerate(document_chunks)}
        self.db.upsert(documents)
        logger.info("Stored {} chunks in the vector database", len(documents))

    def load_documents(self):
        """
        This method loads documents from the specified URIs, chunks them and stores them in a vector database.
        :param overwrite: Whether to overwrite the existing vector database if it exists (default: True).
        """
        chunks = self.chunk()
        self.store(chunks)

    def query(self, 
              query_text:str, 
              top_n:Optional[int]=None, 
              filtering:Literal["F-score-based", "gaussian-mixture-classification"]="F-score-based", 
              **metadata) -> List[str]:
        """
        This method retrieves relevant chunks from the vector database based on a query.
        :param query_text: The query text to search for relevant chunks.
        :param top_n: The number of top relevant chunks to retrieve.
        :return: A list of dictionaries containing the retrieved chunks and their metadata.
        """
        logger.info("Querying context store with query: '{}'", query_text.replace("'", "\\'").replace('"', '\\"'))
        search_result = self.db.top_matches(query_text, top_n, filtering, **metadata)
        matches = search_result["documents"]
        logger.info("Retrieved {} relevant chunks", len(matches))
        return matches


class RetrievalPipeline:
    """
    This class defines a retrieval pipeline that uses a ContextStore to retrieve relevant chunks based on a query.
    It provides methods to rephrase or analyze queries, retrieve and filter or rerank relevant chunks from documents in the context store.
    """
    def __init__(self, 
                 context_store:str=conf["retrieval"]["context_store"], 
                 rephrase_query:bool=conf["retrieval"]["rephrase_query"], 
                 top_n:Optional[int]=conf["retrieval"]["top_n"], 
                 filtering:Literal["F-score-based", "gaussian-mixture-classification"]=conf["retrieval"]["filtering"], 
                 evaluate:bool=conf["retrieval"]["evaluate"], 
                 evaluation:Literal["average", "best-of-n"]=conf["retrieval"]["evaluation"], 
                 **kwargs):
        """
        Initializes the RetrievalPipeline with a ContextStore.
        :param context_store: An instance of ContextStore to be used for retrieval.
        :param rephrase: Whether to rephrase the query to improve retrieval results (default: False).
        :param top_n: The number of top relevant chunks to retrieve (default: None - retrieves all).
        :param filtering: The method to filter or rerank the retrieved results (default: "F_score_based").
        :param evaluate: Whether to evaluate the retrieval results (default: False).
        :param evaluation: The method to evaluate the retrieval results (default: "average").
        """
        logger.info("Initializing RetrievalPipeline with context store at: {}", context_store)
        self.context_store = ContextStore(context_store)
        self.rephrase_query = rephrase_query
        if rephrase_query:
            logger.info("Initializing an LLM for semantic analyses")
            self.expert = llm(semantics_expert)
        self.top_n = top_n
        self.filtering = filtering
        self.evaluate = evaluate
        if self.evaluate:
            logger.info("Using '{}' evaluator for retrieved context", evaluation)
            self.evaluator = llmJudge(task="retrieval", summarize=evaluation, **kwargs)
        else:
            logger.info("Skipping retrieved context evaluation")

    def rephrase(self, query:str) -> str:
        """
        Rephrases the query to improve retrieval results.
        :param query: The original query text.
        :return: The rephrased query text.
        """
        logger.info("Rephrasing query")
        prompter = lambda query: f"""
        Please rephrase the user's query such that it is semantically more similar to the knowledge contained in the attached documents.
        <query>
        {query}
        </query>
        """
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "rephrased_query": {
                    "type": "STRING",
                    "description": "The rephrased query text."
                }
            },
            "required": [
                "rephrased_query"
            ]
        }
        rephrased_query = self.expert.generate(
            prompter(query), 
            response_schema=response_schema, 
            attached_files=self.context_store.document_uris
        )
        rephrased_query = cast(dict, rephrased_query)
        logger.info("Rephrased query: '{}'", rephrased_query["rephrased_query"])
        return rephrased_query["rephrased_query"]

    def retrieve(self, query:str) -> Dict:
        """
        Retrieves relevant chunks based on the provided query.
        :param query: The query text to search for relevant chunks.
        :return: A list of dictionaries containing the retrieved chunks and their metadata.
        """
        logger.info("Retrieving relevant chunks for query: '{}'", query.replace("'", "\\'").replace('"', '\\"'))
        results = {}
        results["query"] = query
        if self.rephrase_query:
            query = self.rephrase(query)
            results["rephrased_query"] = query
        else:
            logger.info("Using original query")
        retrieved_context = self.context_store.query(query, self.top_n, self.filtering) # type: ignore
        results["retrieved_context"] = retrieved_context
        if self.evaluate:
            evaluation_results = self.evaluator([query], [retrieved_context])
            results.update(evaluation_results)
        return results