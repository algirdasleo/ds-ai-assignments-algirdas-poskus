import streamlit as st
from smart_research_assistant.models.constants.openai_models import OPENAI_MODELS
from smart_research_assistant.models.openai.client import OpenAIClient, OpenAIClientConfig
from smart_research_assistant.ui.metrics import display_metrics
from streamlit.delta_generator import DeltaGenerator


async def stream_to_app(
    model_name: str, prompt: str, system_prompt: str | None, output_box: DeltaGenerator, stat_box: DeltaGenerator
) -> None:
    full_text = ""

    def on_stream_update(latest_full_text: str) -> None:
        nonlocal full_text
        full_text = latest_full_text
        output_box.markdown(full_text)

    try:
        client = OpenAIClient(
            OpenAIClientConfig(model_name=str(OPENAI_MODELS[model_name]["label"]), system_prompt=system_prompt)
        )
    except ValueError as e:
        st.error(f"Error initializing OpenAI client: {e}")
        return

    result = await client.get_response(prompt=prompt, on_stream_update=on_stream_update)

    if not result.is_success():
        st.error(f"Error from {model_name}: {result.error}, message: {result.error_message}")
    elif result.data:
        with stat_box.container():
            display_metrics(result.data, model_name, OPENAI_MODELS)
