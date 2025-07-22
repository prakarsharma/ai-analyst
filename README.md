# SAO Chat: LLM-Powered Analytics Tool

## Overview

SAO-chat is a LLM powered conversational analytics and reporting tool. It enables users to interact with data in enterprise BigQuery using natural language. It is implemented as a RAG pipeline to provide the LLM necessary and specific context. It is an agentic framework. The agent can employ a BigQuery client to fetch data necessary to generate a response.

## Features


## Repository Structure

```
sao-chat/
├── app/                # app logic (chatbot, retrieval and generation pipeline, context store, tools, eval, and scripts)
├── models_api/         # LLM, embedding model, vector database, and prompts (system prompt and tools declaration)
├── notebooks/          # Illustrative and development Jupyter notebooks
├── resources/          # Config, schemas, and supporting files
├── utils/              # Utilities (config, logging, database, etc.)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── ...
```

## Runbook

1. **Clone the repository:**
  ```bash
  git clone https://<PAT>@gecgithub01.walmart.com/p0s0a31/ai-analyst.git
  cd ai-analyst
  git checkout -b p0s0a31-working/sao
  git pull origin p0s0a31-working/sao
  git checkout -b <your-branch-name>
  ```

2. **Create an environment**
  ```bash
  conda env create -f env.yml
  pip install -r requirements.txt
  ```

3. **Upload certificates**
  ```bash
  mkdir ../.ssl_certs
  mv ca-bundle.crt ../.ssl_certs/ca-bundle.crt
  ```

## Usage

**Load the vector DB (required if you want to use retrieval or RAG or the NL2SQL agent)**
```bash
nohup env PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd "$(dirname $PWD)/$(basename $PWD)" python -m app.load_vector_store > load.out 2>&1 &
```

- **To generate dynamic insights:**
  ```bash
  nohup env PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd "$(dirname $PWD)/$(basename $PWD)" python -m app.qna --relay <your-relay-name> > outputs.out 2>&1 &
  ```

- **To use the LLM for generation task:**
  ```bash
  PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd "$(dirname $PWD)/$(basename $PWD)" python -m app.test_llm_api --prompt <your-prompt>
  ```

- **To use the retrieval pipeline for retrieval task:**
  ```bash
  PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd "$(dirname $PWD)/$(basename $PWD)" python -m app.retrieve --query <your-query>
  ```

- **To use the RAG pipeline:**
  ```bash
  PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd "$(dirname $PWD)/$(basename $PWD)" python -m app.rag --query <your-query> --get_context
  ```

- **To use the NL2SQL agent:**
  ```bash
  PLATFORM=vertexai GCLOUD_PROJECT_ID=wmt-mtech-assortment-ml-prod conda run -n ai-analyst-env --cwd "$(dirname $PWD)/$(basename $PWD)" python -m app.react --query <your-query> --get_context
  ```

## Configuration


## Key Modules

- `app/main.py`: Chatbot and augmented-generation pipeline (entry point).
- `app/knowledge.py`: Context store and retrieval pipeline.
- `app/functions.py`: Tooling for fetching data and metadata from BigQuery, and results tabulation and visualization.
- `app/eval.py`: Evaluator for retrieval and generation tasks.
- `models_api/generate.py`: LLM
- `models_api/gemini_api.py`: LLM API call payload and chat history storage.
- `models_api/vectorize.py`: Embedding model and vector database.
- `models_api/embedding_api.py`: Embedding model API payload.
- `models_api/function_template.py`: Agent tools declaration.
- `models_api/system_prompt.py`: System prompt.
- `resources/`: Local databases (cost, evaluation and knowledge), metadata on BigQuery tables, and configurations.
- `utils/`: Logging, loading configurations, querying local databases, authentication and other utilities.
- `chat.py`: Streamlit app.

## Development

## Contributing

## License
