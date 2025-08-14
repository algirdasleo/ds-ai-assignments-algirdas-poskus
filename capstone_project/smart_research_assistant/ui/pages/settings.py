import os

import streamlit as st
from dotenv import load_dotenv, set_key

with st.container(border=True):
    st.title("Settings")

    load_dotenv(dotenv_path=".env", override=True)

    if "api_key_input" not in st.session_state:
        saved_key = os.getenv("OPENAI_API_KEY", "")
        st.session_state.api_key_input = saved_key

    api_key = st.text_input("OpenAI API Key", type="password", key="api_key_input")

    if st.button("Save API Key"):
        if not api_key.strip():
            st.error("API key cannot be empty.")
            st.stop()

        set_key(".env", "OPENAI_API_KEY", api_key)
        os.environ["OPENAI_API_KEY"] = api_key
        st.success("API key saved successfully!")
