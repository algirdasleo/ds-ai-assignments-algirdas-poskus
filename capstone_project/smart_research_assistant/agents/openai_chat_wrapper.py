import asyncio
from typing import List, Type, Union

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from smart_research_assistant.models.llm_clients.openai_client import ChatStreamParams, OpenAIChatClient
from smart_research_assistant.types.result.result import ErrorType, Result


class OpenAIChatWrapper(Runnable):
    def __init__(self, client: OpenAIChatClient, model_name="gpt-4.1-mini"):
        self.client = client
        self.model_name = model_name

    async def ainvoke(
        self, input: List[HumanMessage | AIMessage], config=None, **kwargs
    ) -> AIMessage | Result[BaseModel]:
        output_schema: Type[BaseModel] | None = kwargs.get("output_schema", None)

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
                answer_schema=output_schema or None,
            )
        )

        if not result.is_success() or not result.data:
            return Result.fail(result.error or ErrorType.EMPTY_RESULT, result.error_message or "Missing response data")

        if output_schema and result.data and result.data.parsed_response:
            model = result.data.parsed_response
            return Result.ok(model)

        if result.is_success() and result.data:
            return AIMessage(content=result.data.response)
        else:
            raise RuntimeError(f"LLM failed: {result.error}")

    def invoke(
        self, input: List[Union[HumanMessage, AIMessage]], config=None, **kwargs
    ) -> AIMessage | Result[BaseModel]:
        return asyncio.run(self.ainvoke(input, config, **kwargs))
