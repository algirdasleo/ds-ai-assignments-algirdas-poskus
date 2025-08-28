from typing import List

from openai import APIConnectionError, AuthenticationError, BadRequestError, OpenAI, RateLimitError
from smart_research_assistant.configs.config import Settings
from smart_research_assistant.constants.openai_models import OPENAI_EMBEDDING_MODELS
from smart_research_assistant.services.rag_pipeline import EmbeddingModel
from smart_research_assistant.types.result.result import ErrorType, Result

# Pydantic will throw error if any required env vars are missing at runtime
settings = Settings()  # type: ignore


class OpenAIEmbedding(EmbeddingModel):
    def __init__(self, model: OPENAI_EMBEDDING_MODELS = OPENAI_EMBEDDING_MODELS.TEXT_EMBEDDING_3_SMALL):
        self.api_key = settings.openai_api_key
        if not self.api_key:
            raise ValueError("API key is required for OpenAI Models. Set it in the 'Settings' tab or in .env file.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def embed_batch(self, text: List[str]) -> Result[List[List[float]]]:
        try:
            response = self.client.embeddings.create(model=self.enum_to_model_name(), input=text)
            return Result.ok([r.embedding for r in response.data])
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

    def enum_to_model_name(self) -> str:
        return self.model.name.lower().replace("_", "-")
