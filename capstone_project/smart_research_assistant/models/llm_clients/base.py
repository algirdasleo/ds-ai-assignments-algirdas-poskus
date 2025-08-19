from abc import ABC, abstractmethod
from typing import Dict, List

from pydantic import BaseModel
from smart_research_assistant.types.result.response_details import ResponseDetails
from smart_research_assistant.types.result.result import Result
from streamlit.delta_generator import DeltaGenerator


class ChatStreamParams(BaseModel):
    model_name: str
    prompt: str
    stream_box: DeltaGenerator
    messages: List[Dict[str, str]] = []
    api_key: str = ""
    display_model_name: bool = False

    model_config = {"arbitrary_types_allowed": True}


class ChatModel(ABC):
    @abstractmethod
    async def chat_stream(self, params: ChatStreamParams, **kwargs) -> Result[ResponseDetails]:
        raise NotImplementedError
