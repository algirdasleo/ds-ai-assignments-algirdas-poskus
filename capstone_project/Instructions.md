# Model comparison tool - Smart Research Assistant

A stream-lit based app to compare different AI models responses side by side using multiple prompting strategies.

## Features

- Compare two AI models (e.g. OpenAI's GPT-3.5 Turbo and GPT-4) side by side.
- Use different prompting strategies: Zero-shot, Few-shot, Chain of Thought and more.
- Real-time streaming of model responses.
- Cost, usage and time metrics for each model.
- '.env' API key management through the Streamlit interface.

## Installation

### 1. Setup the environment

Install dependencies using Poetry:

```bash
poetry install
```
If you don't have Poetry installed, you can install it using:

```bash
pip install poetry
```

### 2. Add the required environment variables

Create a `.env` file in the root directory of the project and environment variables specified in the .env.example file.

### 3. Create the database tables used for metadata storing

``` bash
poetry run python init_db.py
```

### 4. Run the app

``` bash
poetry run python run.py
```