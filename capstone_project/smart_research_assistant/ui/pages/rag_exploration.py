import asyncio

import streamlit as st
from smart_research_assistant.agents.rag_agent_workflow import RAGAgentWorkflow
from smart_research_assistant.constants.openai_models import OPENAI_EMBEDDING_MODELS, OPENAI_MODELS
from smart_research_assistant.models.embeddings.openai_embedding import OpenAIEmbedding
from smart_research_assistant.services.chunking.semantic_chunking_strategy import SemanticChunking
from smart_research_assistant.services.metadata_stores.sql_metadata_store import SQLMetadataStore
from smart_research_assistant.services.rag_pipeline import RagPipeline, RagPipelineParams
from smart_research_assistant.services.vector_stores.faiss_vector_store import FaissVectorStore

with st.container(border=True):
    with st.container(border=True):
        st.markdown("## RAG Exploration")
        st.markdown("**This page allows you to customize and execute a RAG pipeline.**")

    with st.container(border=True):
        st.markdown("### 1. Pipeline specifications")

        embedding_model = OpenAIEmbedding(OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL)
        vector_store = FaissVectorStore(OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL.value)
        metadata_store = SQLMetadataStore()

        st.markdown(
            f"- OpenAI Embedding Model: {OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL.name} (Dim: {OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL.value})"
        )
        st.markdown(f"- Vector Store: {vector_store.__class__.__name__}")
        st.markdown(f"- Metadata Store: {metadata_store.__class__.__name__}")

        openai_model = st.selectbox("Select OpenAI Chat Model", options=list(OPENAI_MODELS.keys()))

    with st.container(border=True):
        st.markdown("### 2. Build RAG knowledge base")
        st.markdown("**This section allows you to import scientific papers from Arxiv.**")

        st.markdown(f"- Chunking strategy: {SemanticChunking.__name__}")
        with st.expander("Settings"):
            similarity_threshold = st.slider("Sentence Similarity Threshold for Breakpoint creation", 0.0, 1.0, 0.70)
            min_chunk_sentences = st.number_input("Minimum Chunk Size in Sentences", 1, 15, 5)
            overlap_sentences = st.number_input("Overlap Size in Sentences", 0, 10, 3)

        chunking_strategy = SemanticChunking(
            embed_model=embedding_model,
            similarity_threshold=similarity_threshold,
            min_chunk_sentences=min_chunk_sentences,
            overlap_sentences=overlap_sentences,
        )

        col1, col2 = st.columns(2)
        with col1:
            arxiv_query = st.text_input("Enter Arxiv query (topic)", value="Artificial Intelligence")

        with col2:
            n_documents = st.number_input("Enter number of research papers to import", min_value=1, value=5)

        try:
            pipeline = RagPipeline(
                RagPipelineParams(
                    embedding_model=embedding_model,
                    vector_store=vector_store,
                    metadata_store=metadata_store,
                    openai_chat_model=openai_model,
                    chunking_strategy=chunking_strategy,
                )
            )

        except Exception as e:
            st.error(f"Error initializing RAG pipeline: {e}")
            st.stop()

        if st.button("Import Papers"):
            with st.status("Importing Research Papers...", state="running", expanded=True) as status:
                st.write(f'Searching Arxiv for documents with the query: "{arxiv_query}"...')

                def update_status(message: str):
                    st.write(message)

                process_result = pipeline.train(
                    import_query=arxiv_query, n_import_documents=n_documents, update_status=update_status
                )
                if not process_result.is_success():
                    status.update(label="Error during PDF processing.", state="error")
                    st.error(f'Failed to process documents: "{process_result.error_message}"')
                    st.stop()

                status.update(label="PDFs processing finished.", state="complete", expanded=False)

    with st.expander("Reset RAG Knowledge Base", expanded=False):
        if st.button("Reset RAG knowledge Base", type="primary"):
            pipeline.vector_store.reset()
            pipeline.metadata_store.clear()
            st.success("Vector and metadata stores have been reset.")

    with st.container(border=True):
        st.markdown("### 3. Execute RAG Pipeline OR Agent Workflow")
        st.markdown("**This section allows you to execute the RAG pipeline or the RAG Agent Workflow.**")

        col1, col2 = st.columns(2)

        with col1:
            prompt = st.text_area("Enter your prompt here...", height=100, value="Explain GenAI in simple terms.")

        with col2:
            top_k = st.number_input("Number of chunks to retrieve", min_value=1, max_value=20, value=3)

        with st.expander("Context"):
            context_box = st.empty()

        with st.container(border=True):
            result_box = st.caption("Results...")

        with st.expander("Used References"):
            references_box = st.empty()

        if st.button("Run RAG Pipeline"):
            if not prompt:
                st.warning("Please enter a prompt to run the RAG pipeline.")
                st.stop()

            with st.status("Running RAG pipeline...", expanded=True) as status:

                def write_update(message: str):
                    st.write(message)

                retrieval_result = asyncio.run(
                    pipeline.retrieve(prompt, k_embeddings=top_k, stream_box=result_box, update_status=write_update)
                )
                if not retrieval_result.is_success():
                    status.update(label="Error in retrieval", state="error")
                    st.error(f"Retrieval failed: {retrieval_result.error_message}")
                    st.stop()

                if not retrieval_result.data:
                    status.update(label="Error in retrieval", state="error")
                    st.error("No relevant documents found.")
                    st.stop()

                rag_result = asyncio.run(
                    pipeline.generate(
                        query=prompt,
                        metadata=retrieval_result.data,
                        context_box=context_box,
                        result_box=result_box,
                        references_box=references_box,
                        update_status=write_update,
                    )
                )

                if not rag_result.is_success():
                    status.update(label="Error in RAG pipeline", state="error")
                    st.error(f"RAG Pipeline failed: {rag_result.error_message}")
                    st.stop()
                else:
                    status.update(label="RAG pipeline completed successfully.", state="complete", expanded=False)

        if st.button("Run RAG Agent Workflow"):
            with st.expander("Workflow Logs", expanded=True):
                log_box = st.empty()

            rag_agent_workflow = RAGAgentWorkflow(
                rag_pipeline=pipeline,
                log_box=log_box,
                result_box=result_box,
                references_box=references_box,
                context_box=context_box,
            )

            graph_state = asyncio.run(rag_agent_workflow.run(prompt, top_k))
            if not graph_state:
                st.error("RAG Agent Workflow failed.")

            with st.expander("Graph Visualisation"):
                st.image(rag_agent_workflow.graph.get_graph().draw_mermaid_png())
