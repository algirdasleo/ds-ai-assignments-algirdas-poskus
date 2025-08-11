import time
from typing import Callable, List

from openai import APIConnectionError, AsyncOpenAI, AsyncStream, AuthenticationError, BadRequestError, RateLimitError
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam
from pydantic import BaseModel
from smart_research_assistant.configs.env.config import Settings
from smart_research_assistant.models.helpers.message_helper import form_messages
from smart_research_assistant.models.result.result import ErrorType, Result
from smart_research_assistant.models.result.result_details import ResultDetails
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

settings = Settings()


class OpenAIClientConfig(BaseModel):
    model_name: str
    system_prompt: str | None = None
    chat_history: List[ChatCompletionMessageParam] | None = None
    api_key: str | None = None


class OpenAIClient:
    def __init__(self, config: OpenAIClientConfig) -> None:
        self.api_key = config.api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("API key is required. Please set it in the Settings tab or .env file.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model_name = config.model_name
        self.chat_history = form_messages(system_prompt=config.system_prompt, history=config.chat_history)

    async def get_response(
        self,
        prompt: str,
        on_stream_update: Callable[[str], None],
    ) -> Result[ResultDetails]:
        start_time = time.time()
        full_response = ""
        total_tokens = 0
        messages = self.chat_history + [{"role": "user", "content": prompt}]

        try:

            @retry(
                retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
                wait=wait_exponential(multiplier=1, min=2, max=30),
                stop=stop_after_attempt(3),
            )
            async def get_response_with_retry() -> AsyncStream[ChatCompletionChunk]:
                return await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0,
                    stream=True,
                    stream_options={"include_usage": True},
                )

            stream = await get_response_with_retry()

            async for chunk in stream:
                text = extract_chunk_text(chunk)
                full_response += text
                on_stream_update(full_response)

                if chunk.usage and chunk.usage.total_tokens:
                    total_tokens = chunk.usage.total_tokens

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

        total_time = time.time() - start_time

        self.chat_history.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": full_response},
            ]
        )

        await self.client.close()

        return Result.ok(
            ResultDetails(
                model_name=self.model_name,
                response=full_response,
                tokens_used=total_tokens,
                total_time=round(total_time, 2),
            )
        )

    def set_api_key(self, new_api_key: str) -> None:
        if not new_api_key:
            raise ValueError("API key cannot be empty.")
        self.api_key = new_api_key
        self.client = AsyncOpenAI(api_key=self.api_key)


def extract_chunk_text(chunk: ChatCompletionChunk) -> str:
    if not chunk.choices or not chunk.choices[0].delta or not chunk.choices[0].delta.content:
        return ""
    return chunk.choices[0].delta.content
