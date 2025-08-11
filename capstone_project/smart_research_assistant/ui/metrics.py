from typing import Dict

import streamlit as st

from smart_research_assistant.models.result.result_details import ResultDetails


def display_metrics(result_data: ResultDetails, model_name: str, model_info: Dict[str, Dict[str, float | str]]) -> None:
    if not result_data:
        st.warning("No data available for metrics display.")
        return

    if result_data.tokens_used is None:
        st.warning("Token Usage, Cost data can not be found for this model.")
        return

    cost = (result_data.tokens_used * float(model_info[model_name]["price_per_1m_input_tokens"])) / 1_000_000

    col1, col2, col3 = st.columns(3)
    col1.metric("Cost", f"${cost:.5f}")
    col2.metric("Tokens", result_data.tokens_used)
    col3.metric("Time (s)", f"{result_data.total_time:.2f}")
