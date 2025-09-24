import os
import tempfile
import sqlite3
import pandas as pd
import streamlit as st

# --- LangChain backend unique ---
import rag.langchain as rag_backend

st.set_page_config(page_title="RAG PDF Analyzer", page_icon="📄", layout="wide")

# =========================
# 1) SQLite: init + insert
# =========================
def init_db() -> None:
    conn = sqlite3.connect("feedback.db")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            response TEXT,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

def save_feedback(question: str, response: str, feedback: str) -> None:
    conn = sqlite3.connect("feedback.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO feedbacks (question, response, feedback) VALUES (?, ?, ?)",
        (question, response, feedback),
    )
    conn.commit()
    conn.close()

# =========================
# 2) Session state
# =========================
if "stored_files" not in st.session_state:
    st.session_state["stored_files"] = set()   # noms des PDF déjà indexés

# =========================
# 3) UI header
# =========================
st.title("RAG PDF Analyzer")
st.caption("Upload PDFs, index them, and ask grounded questions. Retrieval size is configurable (top-k).")

# =========================
# 4) Upload zone
# =========================
st.subheader("📥 Upload PDFs")
uploaded_files = st.file_uploader(
    label="Drag & drop or select one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

# Tableau récap
file_rows = []

if uploaded_files:
    for f in uploaded_files:
        size_kb = len(f.getvalue()) / 1024
        file_rows.append({"File name": f.name, "Size (KB)": f"{size_kb:.1f}"})

        # Indexer uniquement les nouveaux
        if f.name not in st.session_state["stored_files"]:
            # Sauvegarde temporaire pour passer un path au backend
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, "tmp.pdf")
                with open(pdf_path, "wb") as out:
                    out.write(f.read())
                # Indexation
                try:
                    rag_backend.store_pdf_file(pdf_path, f.name)
                    st.session_state["stored_files"].add(f.name)
                except Exception as e:
                    st.error(f"Indexing failed for {f.name}: {e}")

# Afficher tableau des fichiers sélectionnés cette session
if file_rows:
    st.table(pd.DataFrame(file_rows))
else:
    st.info("No file selected yet. Upload at least one PDF to build your knowledge base.")

# =========================
# 5) Suppression si besoin
# =========================
st.divider()
st.subheader("🗂 Indexed files (this session)")

if st.session_state["stored_files"]:
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.write(", ".join(sorted(st.session_state["stored_files"])))
    with col_b:
        if st.button("Clear index for all files", use_container_width=True, type="secondary"):
            removed_total = 0
            for name in list(st.session_state["stored_files"]):
                try:
                    removed_total += rag_backend.delete_file_from_store(name)
                except Exception as e:
                    st.warning(f"Delete failed for {name}: {e}")
                st.session_state["stored_files"].discard(name)
            st.success(f"Cleared index entries ({removed_total} vectors deleted).")
else:
    st.caption("No document indexed yet in this session.")

# =========================
# 6) QA controls
# =========================
st.divider()
st.subheader("❓ Ask a question")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    language = st.selectbox(
        "Answer language",
        ["français", "anglais", "espagnol", "allemand"],
        index=0
    )
with col2:
    k = st.slider("Top-k retrieval", min_value=1, max_value=10, value=5, step=1)
with col3:
    st.write("")  # spacing
    st.write("")

question = st.text_input("Your question")

# Zone réponse
answer_box = st.empty()

# =========================
# 7) Run QA
# =========================
if st.button("Analyze", type="primary"):
    if not st.session_state["stored_files"]:
        st.warning("Please upload and index at least one PDF first.")
    elif not question.strip():
        st.warning("Please type a non-empty question.")
    else:
        try:
            model_response = rag_backend.answer_question(question, language=language, k=k)
            answer_box.text_area("Model answer", value=model_response, height=200)
            # Feedback
            fb = st.radio("Was this answer helpful?", ["👍 Yes", "👎 No"], horizontal=True, index=0)
            if st.button("Save feedback"):
                save_feedback(question, model_response, fb)
                st.success("Thanks! Your feedback was saved.")
        except Exception as e:
            st.error(f"Answering failed: {e}")
else:
    answer_box.text_area("Model answer", value="", height=200)

# =========================
# 8) Init DB on first load
# =========================
init_db()

# Footer
st.divider()
st.caption("Tip: open **Knowledge Base** in the sidebar to inspect the index.")
