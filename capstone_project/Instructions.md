# Smart Research Assistant Tool

## Features

### Model Comparisons:
- Multiple Local/Cloud models
- Multiple prompting strategies
- Real-time asynchronous answer streaming side-by-side
- 4 key statistics displayed (cost, tokens used, time taken, time to 1st token)

### Local Models:
- Run local models with **Ollama**
- Pick models automatically by using “intelligent” routing according to the keywords and complexity of the prompt.
- Chat using local models with tracking of history.

### RAG & AI Agent Workflow:
- RAG knowledge base - import Arxiv research papers by URL or Query.
- Multiple OpenAI selectable generation models
- Enter a query and execute:
  - **RAG Pipeline** – Searches the downloaded papers for top embeddings similar to prompt
  - **RAG Agent Workflow** – Uses RAG + Web Search for AI/ML related topics and only Web Search for other topics.

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

### 5. Evaluate RAG and Generation performance using DeepEval

``` bash
poetry run python evaluate_rag.py
```

This will run the following tests:
- RAG: PrecisionAtK, ContextualPrecisionMetric, ContextualRelevancyMetric
- Generation: FaithfulnessMetric, AnswerRelevancyMetric
