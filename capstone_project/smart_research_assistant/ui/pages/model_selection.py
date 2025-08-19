import asyncio

import streamlit as st
from smart_research_assistant.helpers.model_selection_helper import get_ollama_models_details, select_model, sort_models
from smart_research_assistant.models.llm_clients.ollama_client import OllamaChatClient
from smart_research_assistant.ui.chat_box import render_chatbox

models = get_ollama_models_details()

sorted_models = sort_models(models)

if "local_messages" not in st.session_state:
    st.session_state.local_messages = []

if not models:
    st.markdown("No local models found. Please install a model using `ollama pull <model_name>`.")
    st.stop()

with st.container(border=True):
    with st.container(border=True):
        st.markdown("## Automatic/Manual Local Model Selection")
        st.markdown("**Run Ollama model either:**")
        st.markdown("-> Selected manually,")
        st.markdown("-> Selected automatically.")

    col1, col2 = st.columns(2, border=True)
    auto_model_checked = False

    with col2:
        st.markdown("### Automatic Model Selection")
        st.caption("Model gets picked automatically according to the complexity of your prompt.")
        auto_model_checked = st.checkbox("Enable Automatic Model Selection")

        if auto_model_checked:
            model_name = None

    with col1:
        st.markdown("### Manual Model Selection")
        model_name = st.selectbox(
            "Choose Installed Ollama Model",
            models.keys(),
            width=300,
            index=None,
            disabled=auto_model_checked,
        )

    if model_name is None and not auto_model_checked:
        st.divider()
        st.stop()

    with col1:
        if model_name is not None and not auto_model_checked:
            for key, value in models[model_name].items():
                st.markdown(f"**{key}**: :blue-badge[ {value}]")

    with st.container(height="content", border=True):
        stat_box = st.caption("Model statistics...")

    with st.container(height=400):
        chatbox_placeholder = st.empty()

    prompt = st.chat_input("Enter your prompt here...")

    if not prompt:
        st.stop()

    if auto_model_checked:
        model_name = select_model(sorted_models, prompt)

    if model_name is None:
        st.warning("Failed to automatically pick the model.")
        st.stop()

    with chatbox_placeholder:
        asyncio.run(
            render_chatbox(
                model=OllamaChatClient(),
                model_name=model_name,
                stat_box=stat_box,
                prompt=prompt,
                display_model_name=True,
                chatbot_id=1,
                model_cost_data={},
            )
        )
