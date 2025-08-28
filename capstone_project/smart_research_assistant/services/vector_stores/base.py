from abc import ABC, abstractmethod
from typing import List

from smart_research_assistant.types.result.result import Result
from smart_research_assistant.types.vector_document import RelevantDocument


class VectorStore(ABC):
    @abstractmethod
    def add(self, doc_id: str, embeddings: List[List[float]]) -> Result[None]:
        """Adds Vector Embeddings for document.

        Returns: Successful or failed Result
        """
        pass

    @abstractmethod
    def search(self, prompt_embedding: List[float], top_k: int) -> Result[List[RelevantDocument]]:
        """Find Top-K similar embeddings

        Returns: Result with a List of Top-K similar embeddings (Document ID, Similarity Score).
        """
        pass

    @abstractmethod
    def save(self) -> Result[None]:
        """Saves the vector store index (and any additional required files) to a folder.

        If not necessary, then return Result.ok() to skip this step
        """
        pass

    @abstractmethod
    def load(self) -> Result[None]:
        """Loads the vector store index (and any additional required files) from a folder.

        If not necessary, then return Result.ok() to skip this step
        """
        pass

    @abstractmethod
    def reset(self) -> Result[None]:
        """Resets the vector store to its initial state.

        If not necessary, then return Result.ok() to skip this step
        """
        pass
