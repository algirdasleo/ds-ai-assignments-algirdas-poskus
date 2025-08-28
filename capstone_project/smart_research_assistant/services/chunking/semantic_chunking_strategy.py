from typing import List, cast

import blingfire
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from smart_research_assistant.models.embeddings.base import EmbeddingModel
from smart_research_assistant.services.chunking.base import ChunkingStrategy
from smart_research_assistant.types.result.result import Result


class SemanticChunking(ChunkingStrategy):
    def __init__(
        self,
        embed_model: EmbeddingModel,
        similarity_threshold: float = 0.75,
        min_chunk_sentences: int = 2,
        overlap_sentences: int = 1,
    ):
        self.embed_model = embed_model
        self.similarity_threshold = similarity_threshold
        self.min_chunk_sentences = min_chunk_sentences
        self.overlap_sentences = overlap_sentences

    def split_sentences(self, text: str) -> List[str]:
        return cast(List[str], blingfire.text_to_sentences(text).split("\n"))

    def chunk(self, text: str) -> Result[List[str]]:
        # Splits sentences using blingfire text_to_sentences, which is a very fast sentence tokenizer
        sentences = self.split_sentences(text)

        if len(sentences) <= self.min_chunk_sentences:
            return Result.ok([text.strip()])

        embeddings_result = self.embed_model.embed_batch(sentences)
        if not embeddings_result.is_success():
            return Result.fail(embeddings_result.error, embeddings_result.error_message)

        embeddings = np.array(embeddings_result.data)

        # For each pair of sequentual sentences, calculate the cosine similarity
        similarities = []
        for i in range(len(embeddings) - 1):
            current_embedding = embeddings[i : i + 1]
            next_embedding = embeddings[i + 1 : i + 2]
            similarity_matrix = cosine_similarity(current_embedding, next_embedding)
            similarity_score = similarity_matrix[0][0]
            similarities.append(similarity_score)

        # Find chunks breakpoints according to the provided similarity threshold
        breakpoints = [i + 1 for i, sim in enumerate(similarities) if sim < self.similarity_threshold]

        # Create chunks based on the breakpoints
        chunks = []
        start = 0
        for breakpoint in breakpoints:
            if breakpoint - start >= self.min_chunk_sentences:
                chunk = " ".join(sentences[start:breakpoint])
                chunks.append(chunk)
                # Moves the start pointer backwards to overlap sentences
                start = max(breakpoint - self.overlap_sentences, start + 1)

        if start < len(sentences):
            chunks.append(" ".join(sentences[start:]))

        return Result.ok(chunks)
