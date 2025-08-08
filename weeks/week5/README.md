# GenAI Data Science Internship: 3-Week Smart Research Assistant Project

## Project Overview

**Duration**: 3 weeks
**Target**: Data science intern with basic NLP experience 
**Deliverable**: Smart Research Assistant that evolves from basic LLM playground to full RAG-powered agent
**Primary Focus**: GenAI concepts and implementation
**Secondary**: Clean code practices 
**Tech Stack**: Python, Poetry, OpenAI API, Ollama, LangGraph, ChromaDB, Streamlit  
**Development Standards**: Black, Ruff, isort

## Learning Objectives

By the end of 3 weeks, the intern will understand:
- LLM API integration and prompt engineering
- Local model deployment via API servers (Ollama / llama.cpp) *and fine-tuning concepts (optional)*
- Vector databases and RAG systems
- Agent architectures and workflow orchestration
- Modern Python development practices and tooling
- Production considerations (cost vs performance tradeoffs) for GenAI applications

---

# Week 5: LLM Foundations & Multi-Model Playground

## Learning Goals
- Master LLM API integration and prompt engineering
- Build foundation for model comparison and evaluation
- Understand model differences (GPT-4 vs e.g. GPT-3.5)
- Learn cost implications of different models
- Establish modern Python development workflow

## Technical Requirements

### Development Setup
- Initialize Poetry project with proper dependency management
- Configure Black, Ruff, isort for code formatting and linting
- Create clean project structure with separation of concerns

### Core Features to Build
1. **Multi-LLM Interface**: Compare GPT-4 and e.g. GPT-3.5 responses side-by-side
2. **Prompt Engineering Lab**: Test different prompting strategies
3. **Cost Tracking System**: Monitor token usage and API costs
4. **Web Interface**: Clean Streamlit (Gradio / Any other) app

### Prompt Engineering Strategies to Implement
- Direct prompting
- Role-based prompting (system messages)
- Few-shot prompting with examples
- Chain-of-thought prompting
- Structured output prompting

### Streamlit Interface Structure
- **Model Lab**: Model comparison with side-by-side responses
- **Prompt Lab**: Prompting strategy testing with performance metrics
- **Sidebar**: API configuration and model parameters

## Assignment Deliverables

**Week 5 Assignment: Multi-LLM Research Playground**

### Requirements
1. **API Integration**
   - OpenAI client with error handling
   - Retry logic (tenacity)
   - Streaming response support

2. **Prompt Engineering Interface**
   - Implementation of 5 different prompt strategies
   - Side-by-side response comparison
   - Response quality metrics (response time, token usage)

3. **Web Interface**
   - Clean Streamlit/Any interface
   - Query input with model selection
   - Response comparison view with metadata

### Success Criteria
- Successfully handles 5-10 diverse test queries across both models
- Demonstrates measurable differences between prompt strategies
- Shows clear cost/performance tradeoffs between models
- Code passes all linting
- *Proper error handling for API failures (optional)*

### Evaluation Dataset
Test with diverse query categories:
- **Factual**: "What is quantum computing?"
- **Analytical**: "Compare supervised vs unsupervised learning approaches"
- **Creative**: "Explain neural networks to a 10-year-old"
- **Complex**: "Analyze ethical implications of AI in healthcare systems"
- **Technical**: "Describe the transformer architecture's attention mechanism"

---

# Week 6: Local Models & "Intelligent" Routing

## Learning Goals
- Deploy and interact with local LLMs via API servers
- Understand model quantization and performance tradeoffs
- Implement cost-effective model routing
- *Experience fine-tuning concepts through external demonstration (optional)*

## Technical Requirements

### Local Model Infrastructure
- **Ollama Setup**: Install and configure Ollama/llama.cpp/... server for local model hosting
- **Model Management**: Pull and serve model locally (Llama 3.1 8B, Gemma 2 9B or 3, IBM Granite, etc.)
- **API Integration**: Simple client for local model communication

### Routing System
- **Query Analysis**: Simple but effective complexity assessment
- **Cost Optimization**: Route queries based on complexity

### Fine-tuning Exploration (optional)
- **External Notebook**: Create Colab/Kaggle demo
- **LoRA Implementation**: Small-scale fine-tuning on summarization task
- **Report**: Clear explanation of fine-tuning process and benefits

## Core Features to Add
1. **Ollama Integration**: Seamless API communication with local Llama model
2. **Query Routing**: Automatic selection between local and cloud models

## Assignment Deliverables

**Week 6 Assignment: Local Model Integration & Intelligent Routing**

### Requirements
1. **Local Model Deployment**
   - Ollama server installation and configuration
   - Llama 3.1-8B model deployment (e.g. with Q4_K_M / Q2_... quants)
   - Clean API client implementation

2. **Intelligent Routing System**
   - Rule-based query complexity assessment
   - Model selection logic
   - *Routing decision logging (optional)*

3. **Enhanced Research Assistant**
   - Integration of local model into existing Week 5 interface
   - Model comparison extended with the local option
   - *Include specialized summarization capability (optional, if fine-tuning)*

4. ***Fine-tuning Demonstration** (optional)*
   - Complete external notebook with LoRA fine-tuning
   - Clear explanation of fine-tuning concepts and applications

### Success Criteria
- Ollama server responds reliably
- Local model generates coherent responses
- Routing system achieves some API cost reduction
- Demonstrate speed vs quality tradeoffs
- *Fine-tuning demonstration shows measurable improvement (optional)*
- All code maintains high quality standards

### Benchmarking Dataset
- same as before or any reasonable

---

# Week 7: RAG System & Agent Architecture

## Learning Goals
- Understand retrieval-augmented generation
- Understand vector databases, similarity search and embedding strategies
- Implement agent workflows with LangGraph
- Create end-to-end research assistant
- Integrate all previous work into cohesive system

## Technical Requirements

### Vector Database Infrastructure
- **DB Setup**: Persistent vector storage (ChromaDB, pgvector. etc.)
- **OpenAI Embeddings**: Embedding generation
- **Document Processing**: Chunking strategy

### RAG Pipeline Implementation
- **Document Ingestion**: Automated processing of research paper corpus
- **Retrieval System**: Similarity search
- **Generation Enhancement**: Context-aware response generation
- **Citation Management**: Proper source attribution

### Agent Architecture
- **LangGraph Integration**: Multi-node workflow orchestration (e.g. route → search → generate)
- **State Management**: Shared state across agent components
- **Tool Integration**: Specialized tools for different tasks
- **Decision Making**: Intelligent routing and task decomposition

## Core Features to Build
1. **Vector Database**: 100+ research papers
2. **RAG Pipeline**: Context retrieval: query → search vector DB → generate with context
3. **Multi-Agent System**: Coordinated workflow with specialized roles (router → retriever → synthesizer)
4. **Complete Integration**: Combination of all previous weeks' work

## Agent Architecture Design

### Agent Workflow Nodes
1. **Router Agent**: Determines query processing strategy (RAG vs direct vs local)
2. **Retrieval Agent**: Searches vector database for relevant context
3. **Synthesis Agent**: Generates responses using retrieved context
4. ***Quality Agent**: Reviews and enhances responses with proper citations (optional)*

### State Management
- **Shared State**: Query, routing decisions, search results, context, responses
- **Step Logging**: Agent decision tracking

### Tool Integration (your choice, here're some examples)
- **Vector Search Tool**: ChromaDB similarity search interface
- **Model Router Tool**: Extended Week 6 routing system
- **Citation Tool**: Automated source formatting

## Assignment Deliverables

**Week 7 Assignment: Complete RAG-Powered Research Agent**

### Requirements
1. **Production Vector Database**
   - Vector  with 100+ research papers (or just abstracts)
   - OpenAI embedding integration
   - Efficient chunking strategy

2. **RAG Implementation**
   - Multi-stage retrieval pipeline
   - Intelligent source selection and citation generation

3. **LangGraph Agent System**
   - Multi-node workflow with clear separation of concerns
   - State management across agent interactions
   - Integration with all previous weeks' model routing
   - Comprehensive logging

4. **Complete Research Assistant**
   - Streamlit interface *with agent step visualization (optional)*
   - Source management
   - Export functionality for research results ("save" button)

### Success Criteria
- Agent successfully handles both RAG and direct queries with appropriate routing
- Provides accurate sources for all retrieved information
- Demonstrates quality improvement over non-RAG responses
- Achieves cost optimization targets from previous weeks

### Test Dataset
Same as before + research questions requiring recent information or reasoning:
- "What are the latest developments in quantum error correction research?"
- "How has transformer architecture evolved since the original attention paper?"
- "Compare recent approaches to AI alignment and safety research"
- "Analyze the relationship between model scale and emergent capabilities"
- "What are the current limitations of large language models in reasoning tasks?"
...
---

# Technical Infrastructure

## Project Structure (example)
```
smart_research_assistant/
├── smart_research_assistant/
│   ├── models/           # LLM management (OpenAI, Ollama)
│   ├── prompts/          # Template management
│   ├── routing/          # Query routing logic
│   ├── rag/             # Vector storage and embeddings
│   ├── agents/          # LangGraph agent implementation
│   └── ui/              # Streamlit interface
├── notebooks/           # Fine-tuning demonstrations (optional)
├── data/               # Research paper corpus
├── pyproject.toml      # Poetry configuration
├── .env                # env variables
└── README.md          # Complete documentation
```

## Dependencies Management
**Core Dependencies**:
- **openai**: LLM and embedding APIs
- **streamlit**: Web interface framework
- **chromadb**: Vector database (or any else)
- **langgraph**: Agent workflow orchestration
- **httpx**: HTTP client for Ollama communication
- **pydantic**: Data validation and typing

**Development Dependencies**:
- **black**: Code formatting
- **ruff**: Fast Python linter
- **isort**: Import sorting

## Development Workflow
1. **Poetry Setup**: Dependency management and virtual environment
2. **Code Quality**: Formatting and linting
4. **Documentation**: Clear README
5. **Version Control**: Git workflow

---

# Evaluation Framework

## Week 5 Assessment
- **API Integration**: Successful multi-model communication
- **Prompt Engineering**: Systematic testing of 5+ strategies with measurable results
- **Interface Quality**: Streamlit app with good UX/UI
- **Code Quality**: Passes all linting and formatting checks
- **Documentation**: Clear code documentation and setup instructions

## Week 6 Assessment
- **Local Deployment**: Ollama server running reliably with model access
- **Routing Implementation**: Working complexity assessment and model selection
- **Cost Optimization**: Demonstrated API cost reduction through routing
- **Integration Quality**: Seamless addition to existing Week 5 functionality

## Week 7 Assessment
- **RAG System**: Functional vector database with accurate retrieval
- **Agent Implementation**: Working LangGraph workflow with proper state management
- **Citation Accuracy**: Proper source attribution
- **Complete Integration**: All previous weeks' work combined

---

## Success Metrics
- **Technical**: All assignments meet success criteria
- **Professional**: Code quality meets standards
- **Learning**: Clear understanding of GenAI concepts and applications
