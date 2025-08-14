from typing import Dict

import streamlit as st
from smart_research_assistant.types.result.response_details import ResponseDetails
from streamlit.delta_generator import DeltaGenerator


def display_metrics(
    result_data: ResponseDetails,
    model_name: str,
    model_info: Dict[str, Dict[str, float]],
    stat_box: DeltaGenerator,
) -> None:
    try:
        cost = round(
            (result_data.tokens_used * float(model_info[model_name]["price_per_1m_input_tokens"])) / 1_000_000, 5
        )
    except Exception:
        cost = "N/A"

    with stat_box:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cost", f"${cost}")
        col2.metric("Tokens", result_data.tokens_used)
        col3.metric("Time taken (s)", f"{result_data.total_time:.2f}")
        col4.metric("Time to 1st token (s)", f"{result_data.time_to_first_token:.4f}")
