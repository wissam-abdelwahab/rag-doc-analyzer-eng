# RAG PDF Analyzer

A **Streamlit** application to analyze PDF documents using **Retrieval-Augmented Generation (RAG)**.  
The goal is to make exploring information inside PDFs fast and intelligent:  
- Upload one or multiple PDF files  
- Text is chunked and indexed in a vector store  
- Ask natural language questions  
- Get grounded answers with supporting passages from the PDFs  

**Typical use cases**:
- Summarize long or technical reports instantly  
- Search for specific information inside large documents  
- Compare multiple PDFs at once  
- Explore research papers or internal documentation  

---

## Quickstart
```bash
# create virtual env
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run app
streamlit run app.py
````

---

## Configuration

Define secrets (e.g. API keys) in `.streamlit/secrets.toml`.
Never hardcode credentials.

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

---

## Project structure

```
.
├── app.py
├── rag/                # backend (langchain.py)
├── pages/              # extra Streamlit pages (optional)
├── samples/            # small example PDFs
├── requirements.txt
└── .gitignore
```

---

## Deploy

1. Push repo to GitHub
2. Connect it to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Set Python version + install from `requirements.txt`
4. Add your secrets in the Streamlit UI
5. Deploy `app.py`

---

## Notes

* Do not commit API keys, keep them in `.streamlit/secrets.toml`
* Keep `samples/` PDFs small (a few MB max)
* Always Clear all outputs before pushing notebooks (if you add any later)

---

## Local test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
