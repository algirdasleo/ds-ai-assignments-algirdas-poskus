from enum import Enum
from typing import Dict

OPENAI_MODELS: Dict[str, Dict[str, float]] = {
    "gpt-4.1": {
        "price_per_1m_input_tokens": 2.00,
        "price_per_1m_output_tokens": 2.00,
    },
    "gpt-4.1-mini": {
        "price_per_1m_input_tokens": 0.40,
        "price_per_1m_output_tokens": 1.60,
    },
    "gpt-3.5-turbo": {
        "price_per_1m_input_tokens": 0.50,
        "price_per_1m_output_tokens": 1.50,
    },
}


class OPENAI_EMBEDDING_MODELS(Enum):
    TEXT_EMBEDDING_3_SMALL = 1536
    TEXT_EMBEDDING_3_LARGE = 3072
