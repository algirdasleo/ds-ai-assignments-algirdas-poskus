from typing import cast

from langchain.schema import AIMessage, SystemMessage
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph
from smart_research_assistant.agents.openai_chat_wrapper import OpenAIChatWrapper
from smart_research_assistant.constants.prompt_templates import (
    ai_ml_topic_check_prompt,
    context_rating_prompt,
    query_improvement_prompt,
)
from smart_research_assistant.db.database import Settings
from smart_research_assistant.helpers.agent_workflow_helper import update_state
from smart_research_assistant.models.llm_clients.openai_client import OpenAIChatClient
from smart_research_assistant.services.rag_pipeline import RagPipeline
from smart_research_assistant.types.agents.agent_state import AgentState
from smart_research_assistant.types.agents.context_rating import ContextRatingModel
from smart_research_assistant.types.agents.prompt_topic import PromptTopicModel
from smart_research_assistant.types.agents.query_improvement import QueryImprovementModel
from smart_research_assistant.types.result.result import Result
from streamlit.delta_generator import DeltaGenerator

settings = Settings()  # type: ignore


class RAGAgentWorkflow:
    def __init__(
        self,
        rag_pipeline: RagPipeline,
        log_box: DeltaGenerator,
        result_box: DeltaGenerator,
        references_box: DeltaGenerator,
        context_box: DeltaGenerator,
    ):
        self.rag_pipeline = rag_pipeline
        self.graph = self._build_graph()
        self.log = log_box
        self.result_box = result_box
        self.references_box = references_box
        self.context_box = context_box
        self.llm = OpenAIChatWrapper(client=OpenAIChatClient(), model_name="gpt-4o")

    async def run(self, rag_prompt: str, k_embeddings: int):
        initial_state: AgentState = {
            "original_query": rag_prompt,
            "k_embeddings": k_embeddings,
            "improved_query": None,
            "retrieved": [],
            "is_ai_ml_related": False,
            "web_search_results": [],
            "needs_web_search": False,
            "web_search_count": 0,
            "answer": "",
            "messages": [],
        }

        try:
            final_state = await self.graph.ainvoke(initial_state)
            return final_state
        except Exception as e:
            update_state(SystemMessage(f"Workflow execution failed: {str(e)}"), initial_state, self.log)
            return initial_state

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("improve_query", self.improve_query)
        builder.add_node("is_ai_ml_related", self.is_ai_ml_related_node)
        builder.add_node("retrieve", self.retrieve_node)
        builder.add_node("web_search", self.web_search_node)
        builder.add_node("context_rating_agent", self.context_rating_agent_node)
        builder.add_node("generate_answer", self.generate_answer_node)

        builder.set_entry_point("improve_query")
        builder.add_edge("improve_query", "is_ai_ml_related")

        def route_after_ai_ml_check(state: AgentState) -> str:
            if state.get("is_ai_ml_related", False):
                return "retrieve"
            else:
                return "web_search"

        builder.add_conditional_edges(
            "is_ai_ml_related",
            route_after_ai_ml_check,
            {
                "retrieve": "retrieve",
                "web_search": "web_search",
            },
        )

        builder.add_edge("retrieve", "context_rating_agent")
        builder.add_edge("web_search", "context_rating_agent")

        def route_after_context_rating(state: AgentState) -> str:
            needs_web_search = state.get("needs_web_search", False)
            web_search_count = state.get("web_search_count", 0)

            # Allow up to 2 web searches to prevent infinite loops
            if needs_web_search and web_search_count < 2:
                return "web_search"
            else:
                return "generate_answer"

        builder.add_conditional_edges(
            "context_rating_agent",
            route_after_context_rating,
            {
                "web_search": "web_search",
                "generate_answer": "generate_answer",
            },
        )

        builder.set_finish_point("generate_answer")

        return builder.compile()

    async def improve_query(self, state: AgentState) -> AgentState:
        update_state(HumanMessage(f"{state.get('original_query')}"), state, self.log)

        improvement_prompt = query_improvement_prompt(state.get("original_query", ""))

        try:
            update_state(SystemMessage("Improving query."), state, self.log)

            result = cast(
                Result[QueryImprovementModel],
                await self.llm.ainvoke([HumanMessage(content=improvement_prompt)], output_schema=QueryImprovementModel),
            )

            if result.is_success() and result.data:
                state["improved_query"] = result.data.improved_query
                update_state(AIMessage(f"Query improved successfully: {state['improved_query']}"), state, self.log)
            else:
                update_state(SystemMessage("Query improvement failed, using original"), state, self.log)
                state["improved_query"] = state["original_query"]

        except Exception as e:
            update_state(SystemMessage(f"Prompt Improvement Failed: {str(e)}"), state, self.log)
            state["improved_query"] = state["original_query"]

        return state

    async def is_ai_ml_related_node(self, state: AgentState) -> AgentState:
        query = state.get("improved_query") or state.get("original_query", "")
        topic_check_prompt = ai_ml_topic_check_prompt(query)
        try:
            update_state(SystemMessage(f"Prompt: {topic_check_prompt}"), state, self.log)
            result = cast(
                Result[PromptTopicModel],
                await self.llm.ainvoke([HumanMessage(content=topic_check_prompt)], output_schema=PromptTopicModel),
            )
            if not result.is_success() or not result.data:
                update_state(SystemMessage("Prompt Topic Check Failed."), state, self.log)
                state["is_ai_ml_related"] = False
                return state

            state["is_ai_ml_related"] = result.data.is_ai_ml_related
            update_state(AIMessage(f"AI/ML Topic Check: {result.data.is_ai_ml_related}"), state, self.log)

        except Exception as e:
            update_state(SystemMessage(f"Prompt Topic Check Failed: {str(e)}"), state, self.log)
            state["is_ai_ml_related"] = False

        return state

    async def retrieve_node(self, state: AgentState) -> AgentState:
        rag_query = state.get("improved_query") or state.get("original_query", "")
        k_embeddings = state.get("k_embeddings", 5)

        update_state(HumanMessage(f"Retrieving documents for: '{rag_query}'"), state, self.log)

        if not rag_query:
            update_state(SystemMessage("RAG Retrieval Failed: No query available"), state, self.log)
            return state

        result = await self.rag_pipeline.retrieve(rag_query, k_embeddings)

        if not result.is_success() or not result.data:
            update_state(SystemMessage(f"RAG Retrieval Failed. Error: {result.error_message}"), state, self.log)
            return state

        state["retrieved"] = result.data
        update_state(SystemMessage("RAG Retrieval Completed Successfully."), state, self.log)

        return state

    async def web_search_node(self, state: AgentState) -> AgentState:
        query = state.get("improved_query") or state.get("original_query", "")

        if not state.get("is_ai_ml_related", False):
            update_state(SystemMessage("Using web search for non AI/ML topic"), state, self.log)
        elif state.get("needs_web_search", False):
            update_state(SystemMessage("Performing web search to gain additional context"), state, self.log)

        try:
            update_state(SystemMessage(f"Starting web search for: {query}"), state, self.log)

            existing_results = state.get("web_search_results", [])
            exclude_urls = []
            for item in existing_results:
                for result in item["results"]:
                    exclude_urls.append(result["url"])

            search = TavilySearch(max_results=5, exclude_urls=exclude_urls)
            results = await search.ainvoke({"query": query})

            if results:
                existing_results.append(results)
                state["web_search_results"] = existing_results

                update_state(SystemMessage("Web Search Completed: Found results"), state, self.log)
            else:
                state["web_search_results"] = []
                update_state(SystemMessage("Web Search Completed: No results found"), state, self.log)

            state["web_search_count"] = state.get("web_search_count", 0) + 1

        except Exception as e:
            update_state(SystemMessage(f"Web Search Failed: {str(e)}"), state, self.log)
            state["web_search_results"] = []
            state["web_search_count"] = state.get("web_search_count", 0) + 1

        return state

    async def context_rating_agent_node(self, state: AgentState) -> AgentState:
        retrieved = state.get("retrieved", [])
        web_results = state.get("web_search_results", [])
        query = state.get("improved_query") or state.get("original_query", "")

        rating_prompt = context_rating_prompt(query, retrieved, web_results)

        try:
            result = cast(
                Result[ContextRatingModel],
                await self.llm.ainvoke([HumanMessage(content=rating_prompt)], output_schema=ContextRatingModel),
            )

            if result.is_success() and result.data:
                state["needs_web_search"] = result.data.needs_web_search

                update_state(AIMessage(f"Web Search Needed: {result.data.needs_web_search}"), state, self.log)
            else:
                state["needs_web_search"] = False
                update_state(
                    SystemMessage(f"Context evaluation failed. Error: {str(result.error_message)}"), state, self.log
                )

        except Exception as e:
            update_state(SystemMessage(f"Context rating failed: {str(e)}"), state, self.log)
            state["needs_web_search"] = False

        return state

    async def generate_answer_node(self, state: AgentState) -> AgentState:
        query = state.get("improved_query") or state.get("original_query", "")
        retrieved = state.get("retrieved", [])
        web_search_results = state.get("web_search_results", [])

        if not query:
            state["answer"] = "No query provided"
            update_state(SystemMessage("No query available for generation"), state, self.log)
            return state

        result = await self.rag_pipeline.generate(
            query=query,
            metadata=retrieved,
            web_search_data=web_search_results,
            context_box=self.context_box,
            result_box=self.result_box,
            references_box=self.references_box,
        )

        state["answer"] = result.data or ""
        update_state(SystemMessage("Answer generated successfully"), state, self.log)
        return state
