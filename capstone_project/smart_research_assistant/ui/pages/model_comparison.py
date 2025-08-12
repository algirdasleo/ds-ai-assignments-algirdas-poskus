import asyncio

import streamlit as st
from smart_research_assistant.constants.openai_models import OPENAI_MODELS
from smart_research_assistant.constants.prompting_strategies import PROMPT_STRATEGIES
from smart_research_assistant.ui.streaming import stream_to_app

with st.container(border=True):
    st.markdown("## Model Comparison Tool")
    st.markdown("Compare outputs from two different models using the same prompt and strategy.")
    st.markdown("---")

    col1_dropdown, col2_dropdown = st.columns(2)

    with col1_dropdown:
        model_name_first = st.selectbox("Choose 1st Model", list(OPENAI_MODELS.keys()), key="model1")

    with col2_dropdown:
        model_name_second = st.selectbox("Choose 2nd Model", list(OPENAI_MODELS.keys()), key="model2")

    prompt_strategy = st.radio(
        label="Select prompt strategy",
        options=PROMPT_STRATEGIES.keys(),
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

    if st.button("Run with Streaming"):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"#### Response from {model_name_first}")
            with st.container(height=120):
                stat_box_1 = st.empty()

            with st.chat_message("ai"):
                output_box_1 = st.empty()

        with col2:
            st.markdown(f"#### Response from {model_name_second}")
            with st.container(height=120):
                stat_box_2 = st.empty()

            with st.chat_message("ai"):
                output_box_2 = st.empty()

        async def run_both_models():
            await asyncio.gather(
                stream_to_app(model_name_first, prompt, system_prompt, output_box_1, stat_box_1),
                stream_to_app(model_name_second, prompt, system_prompt, output_box_2, stat_box_2),
            )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_both_models())
