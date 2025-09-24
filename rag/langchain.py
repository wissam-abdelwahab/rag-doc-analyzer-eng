from __future__ import annotations

from datetime import datetime
import streamlit as st

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

CHUNK_SIZE = 1_000
CHUNK_OVERLAP = 200

# ----------------- Config & guards -----------------
def _get_secret(section: str, key: str) -> str:
    try:
        return st.secrets[section][key]
    except Exception as e:
        raise RuntimeError(
            f"Missing secret `{section}.{key}` in .streamlit/secrets.toml"
        ) from e

config = {
    "chat": {
        "azure_endpoint": _get_secret("chat", "azure_endpoint"),
        "azure_deployment": _get_secret("chat", "azure_deployment"),
        "api_version": _get_secret("chat", "api_version"),
        "azure_api_key": _get_secret("chat", "azure_api_key"),
    },
    "embedding": {
        "azure_endpoint": _get_secret("embedding", "azure_endpoint"),
        "azure_deployment": _get_secret("embedding", "azure_deployment"),
        "api_version": _get_secret("embedding", "api_version"),
        "azure_api_key": _get_secret("embedding", "azure_api_key"),
    },
}

embedder = AzureOpenAIEmbeddings(
    azure_endpoint=config["embedding"]["azure_endpoint"],
    azure_deployment=config["embedding"]["azure_deployment"],
    api_version=config["embedding"]["api_version"],
    api_key=config["embedding"]["azure_api_key"],
)

vector_store = InMemoryVectorStore(embedder)

llm = AzureChatOpenAI(
    azure_endpoint=config["chat"]["azure_endpoint"],
    azure_deployment=config["chat"]["azure_deployment"],
    api_version=config["chat"]["api_version"],
    api_key=config["chat"]["azure_api_key"],
)

# Map: document_name -> set(ids) so we can delete reliably
_DOC_IDS: dict[str, set[str]] = {}
# keep basic metadata alongside _DOC_IDS
_DOC_META: dict[str, str] = {}  # doc_name -> ISO insert_date

# ----------------- Helpers -----------------
def get_meta_doc(extract: str) -> str:
    messages = [
        ("system", "You are a librarian extracting metadata from documents."),
        (
            "user",
            f"""Extract from the content the following metadata.
Answer 'unknown' if you cannot find or generate the information.
Metadata list:
- title
- author
- source
- type of content (e.g. scientific paper, literature, news, etc.)
- language
- themes as a list of keywords

<content>
{extract}
</content>"""
        ),
    ]
    response = llm.invoke(messages)
    return response.content

# ----------------- Public API used by app.py -----------------
def store_pdf_file(file_path: str, doc_name: str, use_meta_doc: bool = True) -> None:
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()  # list[Document]
    if not docs:
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    splits = splitter.split_documents(docs)
    for d in splits:
        d.metadata = {
            "document_name": doc_name,
            "insert_date": datetime.now().isoformat(),
        }

    # Add optional synthetic metadata doc
    if use_meta_doc and splits:
        extract = "\n\n".join(x.page_content for x in splits[: min(10, len(splits))])
        meta_doc = Document(
            page_content=get_meta_doc(extract),
            metadata={
                "document_name": doc_name,
                "insert_date": datetime.now().isoformat(),
            },
        )
        splits.append(meta_doc)

    # Add to vector store and remember the returned IDs
    ids = vector_store.add_documents(documents=splits)  # list[str]
    _DOC_IDS.setdefault(doc_name, set()).update(ids)
    _DOC_META[doc_name] = datetime.now().isoformat()

def delete_file_from_store(name: str) -> int:
    """Delete all vectors belonging to a given document name."""
    ids = list(_DOC_IDS.get(name, []))
    if not ids:
        # Nothing tracked; nothing to delete
        return 0
    vector_store.delete(ids)
    removed = len(ids)
    _DOC_IDS.pop(name, None)
    _DOC_META.pop(name, None)
    return removed

def retrieve(question: str, k: int = 5):
    return vector_store.similarity_search(question, k=k)

def build_qa_messages(question: str, context: str, language: str) -> list[tuple[str, str]]:
    instructions = {
        "français": "Réponds en français.",
        "anglais": "Answer in English.",
        "espagnol": "Responde en español.",
        "allemand": "Antwort auf Deutsch.",
    }
    system_instruction = instructions.get(language, "Answer in English.")
    return [
        ("system", "You are an assistant for question-answering tasks."),
        (
            "system",
            f"""Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.
{system_instruction}
{context}""",
        ),
        ("user", question),
    ]

def answer_question(question: str, language: str = "français", k: int = 5) -> str:
    if not question.strip():
        return "Please provide a non-empty question."
    docs = retrieve(question, k)
    if not docs:
        return "No relevant context found in your documents."
    docs_content = "\n\n".join(doc.page_content for doc in docs)
    messages = build_qa_messages(question, docs_content, language)
    response = llm.invoke(messages)
    return response.content

# ---------- Introspection for the "Knowledge Base" page ----------
def get_vector_store_info() -> dict:
    """High-level info about the in-memory index."""
    num_docs = len(_DOC_IDS)
    num_chunks = sum(len(ids) for ids in _DOC_IDS.values())
    return {
        "backend": "LangChain",
        "documents": num_docs,
        "chunks": num_chunks,
    }

def inspect_vector_store(limit: int = 100):
    """Return a small table (list of dicts) to build a DataFrame in Streamlit."""
    rows = []
    for doc_name, ids in list(_DOC_IDS.items())[:limit]:
        rows.append({
            "document_name": doc_name,
            "chunks": len(ids),
            "insert_date": _DOC_META.get(doc_name, ""),
        })
    return rows


