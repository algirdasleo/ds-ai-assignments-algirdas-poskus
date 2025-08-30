from typing import List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.graph.message import Annotated
from smart_research_assistant.types.metadata import Metadata


class AgentState(TypedDict):
    original_query: str
    k_embeddings: int
    improved_query: str | None
    retrieved: List[Metadata]
    is_ai_ml_related: bool
    web_search_results: List
    needs_web_search: bool
    web_search_count: int
    answer: str

    messages: Annotated[List[BaseMessage], add_messages]
