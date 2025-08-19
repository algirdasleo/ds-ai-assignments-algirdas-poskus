import time

from openai import APIConnectionError, AsyncOpenAI, AsyncStream, AuthenticationError, BadRequestError, RateLimitError
from openai.types.chat import ChatCompletionChunk
from smart_research_assistant.configs.env.config import Settings
from smart_research_assistant.helpers.chat_history_helper import format_messages
from smart_research_assistant.helpers.response_helper import count_tokens, extract_chunk_text
from smart_research_assistant.models.llm_clients.base import ChatModel, ChatStreamParams
from smart_research_assistant.types.result.error_type import ErrorType
from smart_research_assistant.types.result.response_details import ResponseDetails
from smart_research_assistant.types.result.result import Result
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

settings = Settings()


class OpenAIChatClient(ChatModel):
    def __init__(self):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("API key is required for OpenAIChatClient. Set it in the 'Settings' tab or in .env file.")

        self.client = AsyncOpenAI(api_key=self.api_key)

    async def chat_stream(self, params: ChatStreamParams, **kwargs) -> Result[ResponseDetails]:
        if params.display_model_name:
            full_response = f"Selected model: :green-badge[{params.model_name}]. \n\n"
            params.stream_box.write(full_response)
        else:
            full_response = ""

        messages = format_messages(user_prompt=params.prompt, history=params.messages)

        time_start = time.time()
        time_to_first_token = None

        try:

            @retry(
                retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
                wait=wait_exponential(multiplier=1, min=2, max=30),
                stop=stop_after_attempt(3),
            )
            async def get_response_with_retry() -> AsyncStream[ChatCompletionChunk]:
                return await self.client.chat.completions.create(
                    model=params.model_name,
                    messages=messages,
                    temperature=0,
                    stream=True,
                    stream_options={"include_usage": True},
                )

            stream = await get_response_with_retry()

            async for chunk in stream:
                if time_to_first_token is None:
                    time_to_first_token = time.time() - time_start

                text = extract_chunk_text(chunk)
                full_response += text
                params.stream_box.write(full_response)

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

        messages.append({"role": "assistant", "content": full_response})

        return Result.ok(
            ResponseDetails(
                model_name=params.model_name,
                response=full_response,
                time_to_first_token=time_to_first_token or -1,
                total_time=time_taken,
                tokens_used=count_tokens(full_response + params.prompt),
                updated_messages=messages,
            )
        )
