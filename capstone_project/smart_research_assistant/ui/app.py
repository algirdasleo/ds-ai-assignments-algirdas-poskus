import nest_asyncio
import streamlit as st


def launch_app() -> None:
    nest_asyncio.apply()
    st.set_page_config(layout="wide")

    pages = {
        "MODELS": [
            st.Page("ui/pages/model_comparison.py", title="Comparison"),
            st.Page("ui/pages/model_selection.py", title="Auto/Manual Selection"),
        ],
        "RESEARCH ASSISTANCE": [
            st.Page("ui/pages/rag_exploration.py", title="RAG & AI Agent Workflow"),
        ],
        "OTHER": [
            st.Page("ui/pages/settings.py", title="Settings"),
        ],
    }

    pg = st.navigation(pages, position="top")

    pg.run()
