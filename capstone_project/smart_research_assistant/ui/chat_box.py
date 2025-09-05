from typing import Dict

import streamlit as st
from smart_research_assistant.models.llm_clients.base import ChatModel, ChatStreamParams
from smart_research_assistant.ui.metrics import display_metrics
from streamlit.delta_generator import DeltaGenerator


async def render_chatbox(
    model: ChatModel,
    model_name: str,
    prompt: str,
    stat_box: DeltaGenerator,
    api_key: str = "",
    display_model_name: bool = False,
    chatbot_id: int = 1,
    model_cost_data: Dict[str, Dict[str, float]] = {},
) -> None:
    if chatbot_id not in st.session_state:
        st.session_state[chatbot_id] = {"local_messages": []}

    with st.container():
        for msg in st.session_state[chatbot_id]["local_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("ai"):
            stream_box = st.markdown("...")

        params = ChatStreamParams(
            model_name=model_name,
            prompt=prompt,
            stream_box=stream_box,
            messages=st.session_state[chatbot_id]["local_messages"],
            display_model_name=display_model_name,
        )

        result = await model.chat_stream(params)

        if result.data is None or not result.is_success():
            st.error(f"Error occurred while fetching chat response. Reason: {result.error_message}")
            return

        st.session_state[chatbot_id]["local_messages"] = result.data.updated_messages

    display_metrics(result.data, model_name, model_cost_data, stat_box)
