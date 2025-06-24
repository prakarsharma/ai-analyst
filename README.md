# SAO Chat: LLM-Powered Conversational Reporting Tool

## Overview

AI analyst is a Large Language Model (LLM) powered conversational reporting and analytics tool. It enables users to interact with data and knowledge bases using natural language, leveraging retrieval-augmented generation (RAG), semantic search, and integration with BigQuery for advanced data analysis and reporting.

## Features

- **Conversational Analytics**: Query and analyze data using natural language.
- **Retrieval-Augmented Generation (RAG)**: Combines LLMs with vector search for context-aware responses.
- **BigQuery Integration**: Fetch, validate, and analyze data from BigQuery tables.
- **Semantic Search**: Annotate and retrieve document chunks using vector databases.
- **Automated Evaluation**: LLM-based evaluation of generated responses and retrieval quality.
- **Extensible Tooling**: Modular tools for data fetching, table/plot generation, and more.

## Repository Structure

```
sao-chat/
├── app/                # Core application logic (retrieval, augmentation, tools, evaluation)
├── models_api/         # LLM, embedding, and system prompt interfaces
├── notebooks/          # Example and development Jupyter notebooks
├── resources/          # Configurations, schemas, and supporting files
├── utils/              # Utilities (config, logging, database, etc.)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── ...
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd sao-chat
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or use a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

- **Start the application:**
  (Implementation may vary; typically, you would run a main script or use a notebook)
  ```bash
  python -m app.main
  ```
- **Jupyter Notebooks:**
  Explore the `notebooks/` directory for example workflows and usage demos.

## Configuration

- Main configuration is in `resources/config.yml` (edit for data sources, model settings, etc.).
- BigQuery and other credentials should be set up as described in the config and code comments.

## Key Modules

- `app/main.py`: Entry point for the chatbot and generation pipeline.
- `app/knowledge.py`: Context store and retrieval pipeline for semantic search and RAG.
- `app/functions.py`: Tooling for data fetching, validation, and visualization.
- `app/eval.py`: LLM-based evaluation of responses and retrievals.
- `models_api/`: LLM and embedding model interfaces.
- `utils/`: Configuration, logging, and utility functions.

## Development

- Follow standard Python best practices.
- Add new tools or retrieval methods by extending the `app/functions.py` or `app/knowledge.py` modules.
- Use the provided logging and configuration utilities for consistency.

## Contributing

Pull requests and issues are welcome! Please ensure code is well-documented and tested.

## License

[Specify your license here]

---

For more details, see code comments and docstrings throughout the repository.
