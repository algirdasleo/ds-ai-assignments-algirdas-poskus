import time

from openai import (
    APIConnectionError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    NotGiven,
    OpenAI,
    RateLimitError,
)
from openai.lib.streaming.responses import AsyncResponseStreamManager
from pydantic.main import BaseModel
from smart_research_assistant.configs.config import Settings
from smart_research_assistant.helpers.json_helper import extract_streamed_json_values
from smart_research_assistant.helpers.text_processing_helper import count_tokens, format_messages
from smart_research_assistant.models.llm_clients.base import ChatModel, ChatStreamParams
from smart_research_assistant.types.result.error_type import ErrorType
from smart_research_assistant.types.result.response_details import ResponseDetails
from smart_research_assistant.types.result.result import Result
from streamlit.delta_generator import DeltaGenerator
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# Pydantic will throw error if any required env vars are missing at runtime
settings = Settings()  # type: ignore


class OpenAIChatClient(ChatModel):
    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("API key is required for OpenAI Models. Set it in the 'Settings' tab or in .env file.")

        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.client = OpenAI(api_key=self.api_key)

    async def chat_stream(self, params: ChatStreamParams, **kwargs) -> Result[ResponseDetails]:
        if params.display_model_name:
            full_response = f"Selected model: :green-badge[{params.model_name}]. \n\n"
            write_to_stream_box(params.stream_box, full_response)
        else:
            full_response = ""

        parsed_response = None
        time_start = time.time()
        time_to_first_token = None

        try:
            full_response = ""
            parsed_response = None
            stream = await self._get_chat_stream_with_retry(params)
            async with stream as response:
                async for event in response:
                    if time_to_first_token is None:
                        time_to_first_token = time.time() - time_start

                    if event.type == "response.refusal.delta":
                        write_to_stream_box(params.stream_box, "Model refused to respond")
                        return Result.fail(ErrorType.MODEL_REFUSED)
                    elif event.type == "response.error":
                        write_to_stream_box(params.stream_box, f"Error occured: {event.error.message}")
                        return Result.fail(ErrorType.BAD_REQUEST, event.error.message)
                    elif event.type == "response.output_text.delta":
                        full_response += event.delta
                        if params.stream_schema_key:
                            write_to_stream_box(
                                params.stream_box,
                                extract_streamed_json_values(full_response + '"', params.stream_schema_key),
                            )
                        else:
                            write_to_stream_box(params.stream_box, full_response)

                if params.answer_schema is not None and parsed_response is None:
                    final_response = await response.get_final_response()
                    parsed_response = final_response.output_parsed

        except AuthenticationError as e:
            return Result.fail(ErrorType.INVALID_API_KEY, str(e))
        except RateLimitError as e:
            return Result.fail(ErrorType.RATE_LIMIT_EXCEEDED, str(e))
        except BadRequestError as e:
            return Result.fail(ErrorType.BAD_REQUEST, str(e))
        except APIConnectionError as e:
            return Result.fail(ErrorType.CONNECTION_ERROR, str(e))
        except Exception as e:
            return Result.fail(ErrorType.UNHANDLED_EXCEPTION, str(e))

        time_taken = time.time() - time_start

        params.messages.append({"role": "assistant", "content": full_response})

        return Result.ok(
            ResponseDetails(
                model_name=params.model_name,
                response=full_response,
                parsed_response=parsed_response or None,
                time_to_first_token=time_to_first_token or -1,
                total_time=time_taken,
                tokens_used=count_tokens(full_response + params.prompt, params.model_name),
                updated_messages=params.messages,
            )
        )

    async def _get_chat_stream_with_retry(
        self, params: ChatStreamParams
    ) -> AsyncResponseStreamManager[BaseModel] | AsyncResponseStreamManager[NotGiven]:
        @retry(
            retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            stop=stop_after_attempt(3),
        )
        async def _chat_stream_with_retry(
            params: ChatStreamParams,
        ) -> AsyncResponseStreamManager[BaseModel] | AsyncResponseStreamManager[NotGiven]:
            if params.answer_schema is None:
                return self.async_client.responses.stream(
                    model=params.model_name,
                    input=format_messages(user_prompt=params.prompt, history=params.messages),
                    temperature=0,
                )
            else:
                return self.async_client.responses.stream(
                    model=params.model_name,
                    input=format_messages(user_prompt=params.prompt, history=params.messages),
                    temperature=0,
                    text_format=params.answer_schema,
                )

        return await _chat_stream_with_retry(params)


def write_to_stream_box(stream_box: DeltaGenerator | None, content: str) -> None:
    if stream_box:
        stream_box.write(content)
