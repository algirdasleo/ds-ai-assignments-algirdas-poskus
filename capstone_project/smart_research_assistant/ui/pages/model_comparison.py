import asyncio

import streamlit as st
from smart_research_assistant.constants.openai_models import OPENAI_MODELS
from smart_research_assistant.constants.prompting_strategies import PROMPT_STRATEGIES
from smart_research_assistant.helpers.model_selection_helper import get_ollama_models_details
from smart_research_assistant.models.llm_clients.ollama_client import OllamaChatClient
from smart_research_assistant.models.llm_clients.openai_client import OpenAIChatClient
from smart_research_assistant.ui.chat_box import render_chatbox
from streamlit.delta_generator import DeltaGenerator

with st.container(border=True):
    with st.container(border=True):
        st.markdown("## Cloud & Local Models Comparison")
        st.markdown("Compare outputs from two different models using the same prompt and strategy.")

    with st.container(border=True):
        col1_dropdown, col2_dropdown = st.columns(2)

        local_models_details = get_ollama_models_details()

        all_models = {**OPENAI_MODELS, **local_models_details}

        with col1_dropdown:
            model_name_first = st.selectbox("Choose 1st Model", list(all_models.keys()), key="model1")

        with col2_dropdown:
            model_name_second = st.selectbox("Choose 2nd Model", list(all_models.keys()), key="model2")

        prompt_strategy = st.radio(
            label="Select prompt strategy",
            options=list(PROMPT_STRATEGIES.keys()),
        )

        system_prompt = None
        if prompt_strategy == "Role-based Prompt (System Prompt)":
            system_prompt = st.text_area(
                label="System Prompt",
                value="You are a kind teacher who loves explaining science to small children using fun and simple words.",
                height=100,
                key="system_prompt",
            )

        prompt = st.text_area("Alter prompt", value=PROMPT_STRATEGIES[prompt_strategy], height=200)

    if st.button("Run Models"):

        col1, col2 = st.columns(2)

        async def run_and_form_model_response(model_name: str, col: DeltaGenerator) -> None:
            if model_name in local_models_details:
                model = OllamaChatClient()
            else:
                model = OpenAIChatClient()

            with col:
                with st.container(height="content", border=True):
                    stat_box = st.caption("Model statistics...")

                with st.container(height=300):
                    await render_chatbox(
                        model=model,
                        model_name=model_name,
                        stat_box=stat_box,
                        prompt=prompt,
                        chatbot_id=1,
                        model_cost_data={} if model == OllamaChatClient else OPENAI_MODELS,
                    )

        async def run_both_models() -> None:
            await asyncio.gather(
                run_and_form_model_response(model_name_first, col1),
                run_and_form_model_response(model_name_second, col2),
            )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_both_models())
