import pandas as pd
import streamlit as st

# Récupérer le backend courant (défini dans app.py via st.session_state)
backend = st.session_state.get("framework", "langchain")

if backend == "langchain":
    from rag.langchain import inspect_vector_store, get_vector_store_info
elif backend == "llamaindex":
    from rag.llamaindex import inspect_vector_store, get_vector_store_info
else:
    st.error(f"Unsupported backend: {backend}")
    st.stop()

st.set_page_config(
    page_title="Knowledge Base",
    page_icon="🧠",
)

st.title("Knowledge Base")
st.subheader("Visualiser les informations contenues dans la base de connaissances")

# Tableau récapitulatif
st.table(pd.DataFrame.from_dict(get_vector_store_info(), orient="index").transpose())

# Aperçu détaillé
docs_df = inspect_vector_store(100)
st.dataframe(
    docs_df,
    width=1000,
    use_container_width=False,
    hide_index=True,
    column_config={
        "insert_date": st.column_config.DatetimeColumn("Insert Date", format="YYYY-MM-DD"),
    },
)

