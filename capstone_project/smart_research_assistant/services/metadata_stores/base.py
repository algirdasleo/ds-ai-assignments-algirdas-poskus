from abc import ABC, abstractmethod
from typing import List

from smart_research_assistant.types.metadata import Metadata
from smart_research_assistant.types.result.result import Result


class MetadataStore(ABC):
    @abstractmethod
    def upsert(self, doc_id: str, metadata: Metadata) -> Result[None]:
        """Inserts or updates metadata for a Document ID.

        Returns: Successful or Failed Result.
        """
        pass

    @abstractmethod
    def get(self, doc_id: str) -> Result[Metadata]:
        """Retrieves metadata for a Document ID.

        Returns: Result containing Metadata
        """
        pass

    @abstractmethod
    def get_document_ids(self) -> Result[List[str]]:
        """Retrieves all document IDs in the metadata store.

        Returns: Result containing list of document IDs.
        """
        pass

    @abstractmethod
    def clear(self) -> Result[None]:
        """Clears all metadata in the store.

        Returns: Successful or Failed Result.
        """
        pass

    @abstractmethod
    def close(self) -> Result[None]:
        """Closes the metadata store

        Returns: Successful or Failed Result.
        """
        pass
