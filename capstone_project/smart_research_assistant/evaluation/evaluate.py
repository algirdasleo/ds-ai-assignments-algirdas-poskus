import json
from pathlib import Path
import time

from deepeval import evaluate
from deepeval.dataset import EvaluationDataset
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
    AnswerRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from smart_research_assistant.types.result.result import ErrorType, Result
from smart_research_assistant.evaluation.custom_metrics import PrecisionAtK
from smart_research_assistant.models.embeddings.openai_embedding import (
    OPENAI_EMBEDDING_MODELS,
    OpenAIEmbedding,
)
from smart_research_assistant.services.chunking.semantic_chunking_strategy import SemanticChunking
from smart_research_assistant.services.metadata_stores.sql_metadata_store import SQLMetadataStore
from smart_research_assistant.services.rag_pipeline import RagPipeline, RagPipelineParams
from smart_research_assistant.services.vector_stores.faiss_vector_store import FaissVectorStore

K_EMBEDDINGS = 3


async def run_rag_evaluation() -> Result[None]:
    try:
        print("Creating RAG pipeline...")
        embedding_model = OpenAIEmbedding(OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL)

        pipeline = RagPipeline(
            RagPipelineParams(
                embedding_model=embedding_model,
                vector_store=FaissVectorStore(OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL.value),
                metadata_store=SQLMetadataStore(),
                openai_chat_model="gpt-4o-mini",
                chunking_strategy=SemanticChunking(embedding_model, 0.6, 3, 2),
            )
        )

        print("Loading test cases...")
        dataset = EvaluationDataset()

        with open(Path(__file__).parent / "test_cases.json") as f:
            data = json.load(f)

        for i, case in enumerate(data):
            query = case["input"]
            expected_output = case["expected_output"]
            arxiv_ids = case["arxiv_ids"]

            pipeline.ingest_documents_from_links(arxiv_ids)

            metadata = await pipeline.retrieve(query, k_embeddings=K_EMBEDDINGS)
            if not metadata or not metadata.data:
                continue

            retrieved_chunks = [chunk.content for doc in metadata.data for chunk in doc.chunks]

            test_case = LLMTestCase(
                input=query,
                expected_output=expected_output,
                retrieval_context=retrieved_chunks,
                additional_metadata={
                    "retrieved_arxiv_ids": [doc.document.doc_id.split("v")[0] for doc in metadata.data],
                    "expected_arxiv_ids": arxiv_ids,
                },
            )

            print(f"- {i + 1} Test case added")

            dataset.add_test_case(test_case)

        print("Evaluating test cases...")

        if len(dataset.test_cases) > 1:
            # Adding delays to avoid being rate limited
            time.sleep(5)

        evaluate(
            test_cases=dataset.test_cases,
            metrics=[PrecisionAtK(), ContextualPrecisionMetric(), ContextualRelevancyMetric()],
        )

        return Result.ok(None)

    except Exception as e:
        return Result.fail(ErrorType.UNHANDLED_EXCEPTION, str(e))


async def run_generate_evaluation() -> Result[None]:
    try:
        print("Creating RAG pipeline...")
        embedding_model = OpenAIEmbedding(OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL)

        pipeline = RagPipeline(
            RagPipelineParams(
                embedding_model=embedding_model,
                vector_store=FaissVectorStore(OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL.value),
                metadata_store=SQLMetadataStore(),
                openai_chat_model="gpt-4o-mini",
                chunking_strategy=SemanticChunking(embedding_model, 0.6, 3, 2),
            )
        )

        print("Loading test cases...")
        dataset = EvaluationDataset()

        with open(Path(__file__).parent / "test_cases.json") as f:
            data = json.load(f)

        for i, case in enumerate(data):
            query = case["input"]
            arxiv_ids = case["arxiv_ids"]

            pipeline.ingest_documents_from_links(arxiv_ids)

            metadata = await pipeline.retrieve(query, k_embeddings=K_EMBEDDINGS)
            if not metadata or not metadata.data:
                print("No metadata retrieved, skipping test case.")
                continue

            retrieved_chunks = [chunk.content for doc in metadata.data for chunk in doc.chunks]

            generate_result = await pipeline.generate(query=query, metadata=metadata.data)
            if not generate_result or not generate_result.data:
                print("No generation result retrieved, skipping test case.")
                continue

            test_case = LLMTestCase(
                input=query,
                actual_output=generate_result.data,
                retrieval_context=retrieved_chunks,
            )

            print(f"- {i + 1} Test case added")

            dataset.add_test_case(test_case)

        print("Evaluating test cases...")

        if len(dataset.test_cases) > 1:
            # Adding delays to avoid being rate limited
            time.sleep(10)

        evaluate(
            test_cases=dataset.test_cases,
            metrics=[FaithfulnessMetric(), AnswerRelevancyMetric()],
        )

        return Result.ok(None)

    except Exception as e:
        return Result.fail(ErrorType.UNHANDLED_EXCEPTION, str(e))
