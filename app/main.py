from typing import Dict

from models_api.system_prompt import data_analyst
from models_api.function_template import tools
from models_api.gemini_api import chat_request, chat_api_message
from models_api.generate import llm
from app.functions import Tools
from app.knowledge import RetrievalPipeline
from app.eval import llmJudge
from app.history import history
from utils.cert import load_wmt_ca_bundle
from utils.config import conf
from utils.logging import logger


class chatbot:
    def __init__(self, 
                 timestamp:str, 
                 max_react_iterations:int=10):
        """
        Initializes the chatbot.
        :param timestamp: A timestamp in the format YYYYMMDD_HHMMSS.
        :param max_react_iterations: The maximum number of iterations for the chatbot to react to user input (default: 10).
        """
        logger.info("Initializing chatbot at: {}", timestamp)
        logger.info("Setting max react iterations to: {}", max_react_iterations)
        self.max_react_iterations = max_react_iterations
        load_wmt_ca_bundle()
        self.generation_pipeline = AugmentedGenerationPipeline(system_prompt=data_analyst, experiment=f"experiment_{timestamp}")
        self.generation_pipeline.add_retriever(experiment=f"experiment_{timestamp}")
        self.chat = chat_api_message()

    def answer(self, 
               query:str, 
               get_context:bool=False, 
               analyze:bool=False, 
               plan:bool=False) -> Dict:
        try:
            logger.success("User: {}", query)
            prompt = self.generation_pipeline.prompt(query,
                                                     retrieval_augmentation=get_context, 
                                                     analysis_augmentation=analyze,
                                                     thought_augmentation=plan)
            self.chat.append("user", prompt)
            response = {}
            for i in range(self.max_react_iterations):
                response = self.generation_pipeline.generate_chat(self.chat)
                logger.success("Chatbot: {}", response["response"])
                self.chat.append("model", **response)
                if response["mode"] == "functionCall":
                    response = self.generation_pipeline.use_tool(**response["response"])
                    if response.get("EOS"):
                        break
                    else:
                        logger.success("FunctionCall: {}", response)
                        self.chat.append("model", **response)
            return response
        except (ValueError, ConnectionError) as err:
            logger.error("{} | {}", type(err).__name__, err.args[0], exc_info=True)
            self.chat.pop()
            raise err

    def capture(self, mode:str, message):
        logger.info("{} | {}", mode, message)


class AugmentedGenerationPipeline:
    """
    This class defines an augmented-generation pipeline. It uses an LLM to generate responses based on a given prompt. 
    The responses can be augmented by a retiever, an analyzer or a long-context.
    """
    def __init__(self, 
                 system_prompt:str, 
                 use_reminder:bool=conf["generation"]["use_reminder"], 
                 evaluate:bool=conf["generation"]["evaluate"], 
                 **kwargs):
        """
        Initializes the AugmentedGenerationPipeline with an LLM.
        :param model: LLM name (default: 'gemini-2.0-flash-001').
        :param system_prompt: The system prompt to the LLM.
        :param tools: List of tools to be used by the LLM in OpenAPI schema (default: empty list).
        :param use_validation: Whether to validate the generated queries (default: True).
        :param use_reminder: Whether to send a reminder at query generation (default: True).
        :param evaluate: Whether to evaluate the generated response (default: False).
        """
        logger.info("Initializing pipeline with LLM '{}'", conf["models"]["llm"]["name"])
        self.model = llm(system_prompt, tools=tools)
        self.tools = tools
        self.functions = Tools(use_reminder)
        self.evaluate = evaluate
        if self.evaluate:
            logger.info("Using an evaluator for generated content")
            self.evaluator = llmJudge(task="generation", **kwargs)
        else:
            logger.info("Skipping generated content evaluation")

    def add_retriever(self, **kwargs):
        """
        Adds a retrieval pipeline to the generation pipeline.
        """
        self.retrieval_pipeline = RetrievalPipeline(**kwargs)

    def add_analyzer(self):
        """
        Adds a query analyzer to the generation pipeline.
        """
        self.analyzer = None

    def prompt(self, 
               query:str, 
               retrieval_augmentation:bool=False, 
               analysis_augmentation:bool=False, 
               thought_augmentation:bool=False, 
               **kwargs) -> str:
        """
        Generates an augmented prompt to facilitate LLM response.
        :param retrieval_augmentation: Whether to augment the prompt with retrieval results (default: False).
        :param analysis_augmentation: Whether to augment the prompt with analysis results (default: False).
        :param thought_augmentation: Whether to augment the prompt with a thought process (default: False).
        :param kwargs: Additional keyword arguments for the prompt.
        :return: A dictionary containing the generated prompt.
        """
        logger.info("Generating prompt for query: '{}'", query.replace("'", "\\'").replace('"', '\\"'))
        prompt_builder = f"Query: {query}"
        if retrieval_augmentation:
            if hasattr(self, "retrieval_pipeline"):
                logger.info("Detected retrieval pipeline. Augmenting prompt with retrieved context")
                retrieval_results = self.retrieval_pipeline.retrieve(query)
                # response["retrieval_results"]  = retrieval_results
                added_context = retrieval_results.get("retrieved_context", [])
                augment = f"""""\n Respond to the prompt given the following context:\n\n {added_context}"""
                prompt_builder += augment
            else:
                logger.warning("No retrieval pipeline found. Skipping retrieval augmentation. Add a retrieval pipeline using `add_retriever` method.")
        else:
            logger.info("Skipping retrieval augmentation")
        if analysis_augmentation:
            if hasattr(self, "analyzer"):
                logger.info("Detected query analyzer. Augmenting prompt with analysis")
                # analysis_results = self.analyzer.analyze(query)
                # response["analysis_results"] = analysis_results
                # analysis = analysis_results.get("analysis", "")
                # augment = f"""
                # Respond to the prompt given the following analysis:

                # {analysis}"""
                # prompt_builder += augment
            else:
                logger.warning("No query analyzer found. Skipping analysis augmentation. Add an analyzer using `add_analyzer` method.")
        else:
            logger.info("Skipping analysis augmentation")
        if thought_augmentation:
            logger.info("Augmenting prompt with planning")
            augment = f"\n Come up with a plan to answer the query and lay down your entire thought process step-by-step.\n"
            prompt_builder += augment
        else:
            logger.info("Skipping planning")
        logger.info("Prompt:\n{}", prompt_builder)
        return prompt_builder

    def generate_chat(self, chat:chat_api_message, force_function_call=False, **kwargs) -> Dict:
        logger.info("Generating response")
        if force_function_call:
            kwargs["allowed_function_names"] = [tool["name"] for tool in self.tools]
        response_object = self.model.request(chat.messages, **kwargs)
        response = chat_request.parse_response(response_object)
        if self.evaluate:
            evaluation_results = self.evaluator([str(chat)], [response["response"]])
            response.update(evaluation_results)
        return response

    def use_tool(self, name:str, args:Dict, **kwargs) -> Dict:
        """
        Uses the tools defined in the pipeline to perform actions.
        """
        response = {}
        if name:
            function_return_object = getattr(self.functions, name).__call__(**args, **kwargs)
            if name in ["table", "plot", "EOS"]:
                response["EOS"] = True
                response[name] = function_return_object
            else:
                response = chat_request.function_response(name, function_return_object)
                # if "query" in args:
                    # response["query"] = args["query"]
        return response