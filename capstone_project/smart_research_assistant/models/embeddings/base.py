from abc import ABC, abstractmethod
from typing import List

from smart_research_assistant.types.result.result import Result


class EmbeddingModel(ABC):
    @abstractmethod
    def embed_batch(self, text: List[str]) -> Result[List[List[float]]]:
        pass
