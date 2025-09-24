# RAG PDF Analyzer

A Streamlit application to analyze PDF documents using Retrieval-Augmented Generation (RAG).  
Upload PDFs, build a vector index, retrieve top-k chunks, and generate grounded answers.

## Features
- Multi-PDF upload and on-the-fly chunking
- Backend switch: LangChain or LlamaIndex
- Answer language selector (EN/FR/ES/DE)
- Configurable top-k retrieval
- User feedback stored in SQLite
- One-click deploy on Streamlit Community Cloud

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Define secrets (e.g. API keys) in `.streamlit/secrets.toml`. Never hardcode credentials.

Example:

```toml
[chat]
azure_endpoint   = "https://YOUR-AZURE-RESOURCE.openai.azure.com/"
azure_deployment = "YOUR-CHAT-DEPLOYMENT-NAME"
api_version      = "2024-02-01"
azure_api_key    = "YOUR-CHAT-KEY"

[embedding]
azure_endpoint   = "https://YOUR-AZURE-RESOURCE.openai.azure.com/"
azure_deployment = "YOUR-EMBEDDING-DEPLOYMENT-NAME"
api_version      = "2024-02-01"
azure_api_key    = "YOUR-EMBEDDING-KEY"
```

## Project structure

```
.
├── app.py
├── rag/                # backends (langchain.py, llamaindex.py, etc.)
├── pages/              # extra Streamlit pages (optional)
├── notebooks/          # demos/experiments (outputs cleared)
├── samples/            # small example PDFs only
├── requirements.txt
└── .gitignore
```

## Deploy

Connect this repository to Streamlit Community Cloud, set Python version and secrets, and deploy `app.py`.

## Notes

* `rag/` must contain `__init__.py`, `langchain.py`, and `llamaindex.py`.
* Do **not** commit API keys → keep them in `.streamlit/secrets.toml`.
* Keep `samples/` PDFs small (a few MB).
* Always “Clear all outputs” in notebooks before pushing.

## Local test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

* Upload 1–2 PDFs from `samples/`
* Ask a question → check that a model answer is returned
* Verify that `feedback.db` is created and feedback is stored
