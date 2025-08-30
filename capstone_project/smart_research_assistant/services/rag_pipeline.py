from typing import Callable, Dict, List

from pydantic import BaseModel
from smart_research_assistant.constants.prompt_templates import generate_answer_prompt
from smart_research_assistant.helpers.research_paper_helper import gather_documents
from smart_research_assistant.helpers.text_processing_helper import (
    extract_text_from_pdf,
    form_context,
    write_references,
)
from smart_research_assistant.models.embeddings.base import EmbeddingModel
from smart_research_assistant.models.llm_clients.openai_client import OpenAIChatClient
from smart_research_assistant.services.chunking.base import ChunkingStrategy
from smart_research_assistant.services.metadata_stores.base import MetadataStore
from smart_research_assistant.services.vector_stores.base import VectorStore
from smart_research_assistant.types.metadata import ChunkMetadata, Metadata
from smart_research_assistant.types.rag_answer import AnswerModel
from smart_research_assistant.types.result.result import ErrorType, Result
from smart_research_assistant.ui.chat_box import ChatStreamParams
from streamlit.delta_generator import DeltaGenerator


class RagPipelineParams(BaseModel):
    embedding_model: EmbeddingModel
    vector_store: VectorStore
    metadata_store: MetadataStore
    openai_chat_model: str
    chunking_strategy: ChunkingStrategy

    model_config = {"arbitrary_types_allowed": True}


class RagPipeline:
    def __init__(self, params: RagPipelineParams):
        self.embedding_model = params.embedding_model
        self.vector_store = params.vector_store
        self.metadata_store = params.metadata_store
        self.openai_chat_model = params.openai_chat_model
        self.chunking_strategy = params.chunking_strategy

        vector_load_result = self.vector_store.load()
        if not vector_load_result.is_success():
            raise ValueError(f"Failed to load vector store: {vector_load_result.error_message}")

    def train(
        self,
        import_query: str | None,
        n_import_documents: int | None = 10,
        update_status: Callable[[str], None] | None = None,
    ) -> Result[None]:
        if not import_query or not n_import_documents:
            return Result.ok(None)

        search_result = gather_documents(self.metadata_store, import_query, n_import_documents)
        if search_result.is_success():
            new_docs_metadata = search_result.data or []
        else:
            new_docs_metadata = []

        try:
            for doc_metadata in new_docs_metadata:
                try:
                    # 1. Extract text from PDF
                    send_status_update(f'Processing document: "{doc_metadata.title}"', update_status)
                    extracted_text = extract_text_from_pdf(doc_metadata)

                    # 2. Chunk text
                    chunks_result = self.chunking_strategy.chunk(extracted_text)
                    if not chunks_result.is_success():
                        raise ValueError(f"Failed to chunk text: {chunks_result.error_message}")
                except Exception as _:
                    send_status_update(f"Failed to process document: {doc_metadata.title}", update_status)
                    continue

                chunks = chunks_result.data or []

                # 3. Embed chunks
                embeddings_result = self.embedding_model.embed_batch(chunks)
                if not embeddings_result.is_success():
                    raise ValueError(f"Failed to embed chunks: {embeddings_result.error_message}")

                embeddings = embeddings_result.data or []

                # 4. Create chunk metadata
                chunk_metadata = [
                    ChunkMetadata(doc_id=doc_metadata.doc_id, chunk_index=i, content=chunk)
                    for i, chunk in enumerate(chunks)
                ]

                # 5. Form Document + Chunks metadata
                complete_metadata = Metadata(document=doc_metadata, chunks=chunk_metadata)

                # 6. Store embeddings and metadata
                vector_result = self.vector_store.add(doc_metadata.doc_id, embeddings)
                if not vector_result.is_success():
                    raise ValueError(f"Failed to add embeddings to vector store: {vector_result.error_message}")

                metadata_result = self.metadata_store.upsert(doc_metadata.doc_id, complete_metadata)
                if not metadata_result.is_success():
                    raise ValueError(f"Failed to upsert metadata: {metadata_result.error_message}")

            # 8. Save stores and close connections
            self.vector_store.save()
            self.metadata_store.close()

            return Result.ok(None)
        except Exception as e:
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, str(e))

    async def retrieve(
        self,
        query: str,
        k_embeddings: int = 5,
        stream_box: DeltaGenerator | None = None,
        update_status: Callable[[str], None] | None = None,
    ) -> Result[List[Metadata]]:
        send_status_update("Embedding user prompt...", update_status)
        # 1. Embed user prompt
        embedding_result = self.embedding_model.embed_batch([query])
        if not embedding_result.is_success() or not embedding_result.data:
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, embedding_result.error_message)

        query_embedding = embedding_result.data[0]

        send_status_update("Performing similarity search...", update_status)
        # 2. Perform similarity search in vector store to find K top embeddings
        vector_result = self.vector_store.search(query_embedding, top_k=k_embeddings)

        if not vector_result.is_success() or not vector_result.data:
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, vector_result.error_message or "No similar vectors found.")

        send_status_update("Filtering relevant documents...", update_status)
        # 3. Filter most relevant documents
        relevant_docs = [doc for doc in vector_result.data if doc.similarity_score > 0.5]
        if not relevant_docs:
            await self.inform_user_of_no_results(stream_box)
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, "No relevant documents found")

        send_status_update("Retrieving documents metadatas...", update_status)
        # 4. For each relevant document, retrieve its metadata
        metadata: List[Metadata] = []
        for doc in relevant_docs:
            metadata_result = self.metadata_store.get(doc.doc_id)
            if not metadata_result.is_success() or not metadata_result.data:
                return Result.fail(ErrorType.RAG_PIPELINE_ERROR, metadata_result.error_message or "No metadata found")

            chunks = metadata_result.data.chunks
            if doc.chunk_id >= len(chunks):
                return Result.fail(
                    ErrorType.RAG_PIPELINE_ERROR,
                    f"chunk_id {doc.chunk_id} out of range (total chunks: {len(chunks)}) for doc_id {doc.doc_id}",
                )

            relevant_chunk = chunks[doc.chunk_id]
            metadata.append(Metadata(document=metadata_result.data.document, chunks=[relevant_chunk]))

        if not metadata:
            await self.inform_user_of_no_results(stream_box)
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, "No relevant metadata found")

        return Result.ok(metadata)

    async def generate(
        self,
        query: str,
        metadata: List[Metadata],
        web_search_data: List[Dict[str, str]] = [],
        context_box: DeltaGenerator | None = None,
        result_box: DeltaGenerator | None = None,
        references_box: DeltaGenerator | None = None,
        update_status: Callable[[str], None] | None = None,
    ) -> Result[str]:
        try:
            send_status_update("Creating LLM prompt with context...", update_status)
            # 1. Create context
            context = form_context(metadata, web_search_data)
            if context_box:
                context_box.write(context)

            send_status_update("Generating answer...", update_status)
            # 2. Generate answer
            answer = await OpenAIChatClient().chat_stream(
                ChatStreamParams(
                    model_name=self.openai_chat_model,
                    prompt=generate_answer_prompt(context, query),
                    stream_box=result_box,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a research assistant helping answer questions using referencing retrieved papers and web search content.",
                        }
                    ],
                    answer_schema=AnswerModel,
                    stream_schema_key="answer",
                )
            )
            if not answer.is_success() or answer.data is None:
                return Result.fail(ErrorType.RAG_PIPELINE_ERROR, answer.error_message or "No answer generated")

            if answer.data.parsed_response and isinstance(answer.data.parsed_response, AnswerModel):
                write_references(answer.data.parsed_response, references_box)
            else:
                return Result.fail(ErrorType.RAG_PIPELINE_ERROR, "Received invalid model from OpenAI")

            return Result.ok(answer.data.response)
        except Exception as e:
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, str(e))

    async def inform_user_of_no_results(self, stream_box: DeltaGenerator | None):
        if not stream_box:
            return
        return await OpenAIChatClient().chat_stream(
            ChatStreamParams(
                model_name=self.openai_chat_model,
                prompt="Inform the user that we do not have the user in the database.",
                stream_box=stream_box,
                messages=[],
            )
        )


def send_status_update(message: str, update_status: Callable[[str], None] | None = None):
    if update_status:
        update_status(message)
