import nest_asyncio
import streamlit as st


def launch_app() -> None:
    nest_asyncio.apply()
    st.set_page_config(layout="wide")

    pages = {
        "Models": [
            st.Page("ui/pages/model_comparison.py", title="Cloud Models Comparison"),
            st.Page("ui/pages/local_models.py", title="Local Model Execution"),
        ],
        "Other": [
            st.Page("ui/pages/settings.py", title="Settings"),
        ],
    }

    pg = st.navigation(pages)

    pg.run()
