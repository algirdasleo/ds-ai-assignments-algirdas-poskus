from typing import List, Union

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from smart_research_assistant.models.llm_clients.openai_client import ChatStreamParams, OpenAIChatClient


class OpenAIChatWrapper(Runnable):
    def __init__(self, client: OpenAIChatClient, model_name="gpt-4o"):
        self.client = client
        self.model_name = model_name

    async def ainvoke(self, input: List[Union[HumanMessage, AIMessage]], config=None, **kwargs) -> AIMessage:
        history = []
        prompt = ""
        for msg in input:
            if isinstance(msg, HumanMessage):
                prompt = msg.content
            else:
                history.append({"role": "assistant", "content": msg.content})

        result = await self.client.chat_stream(
            ChatStreamParams(
                prompt=str(prompt),
                model_name=self.model_name,
                messages=history,
            )
        )

        if result.is_success() and result.data:
            return AIMessage(content=result.data.response)
        else:
            raise RuntimeError(f"LLM failed: {result.error}")

    def invoke(self, input: List[Union[HumanMessage, AIMessage]], config=None, **kwargs) -> AIMessage:
        import asyncio

        return asyncio.run(self.ainvoke(input))
