import time

from smart_research_assistant.helpers.chat_history_helper import format_messages
from smart_research_assistant.helpers.response_helper import count_tokens
from smart_research_assistant.models.llm_clients.base import ChatModel, ChatStreamParams
from smart_research_assistant.types.result.error_type import ErrorType
from smart_research_assistant.types.result.response_details import ResponseDetails
from smart_research_assistant.types.result.result import Result

from ollama import AsyncClient


class OllamaChatClient(ChatModel):
    async def chat_stream(self, params: ChatStreamParams, **kwargs) -> Result[ResponseDetails]:
        if params.display_model_name:
            full_response = f"Selected model: :green-badge[{params.model_name}]. \n\n"
            params.stream_box.write(full_response)
        else:
            full_response = ""

        params.messages = format_messages(user_prompt=params.prompt, history=params.messages)

        time_to_first_token = None
        time_start = time.time()

        try:
            client = AsyncClient(host="http://ollama:11434")

            async for chunk in await client.chat(
                model=params.model_name,
                messages=params.messages,
                stream=True,
            ):
                if time_to_first_token is None:
                    time_to_first_token = time.time() - time_start

                full_response += chunk["message"]["content"]
                params.stream_box.write(full_response)

        except Exception as e:
            params.stream_box.error(f"Error while streaming response: {e}")
            return Result.fail(ErrorType.UNHANDLED_EXCEPTION, str(e))

        time_taken = time.time() - time_start

        params.messages.append({"role": "assistant", "content": full_response})

        return Result.ok(
            ResponseDetails(
                model_name=params.model_name,
                response=full_response,
                time_to_first_token=time_to_first_token or -1,
                total_time=time_taken,
                tokens_used=count_tokens(full_response + params.prompt),
                updated_messages=params.messages,
            )
        )
