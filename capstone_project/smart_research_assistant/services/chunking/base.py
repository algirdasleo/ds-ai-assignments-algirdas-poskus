from abc import ABC, abstractmethod
from typing import List

from smart_research_assistant.types.result.result import Result


class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> Result[List[str]]:
        pass
