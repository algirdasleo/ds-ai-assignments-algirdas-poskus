from typing import Dict

OPENAI_MODELS: Dict[str, Dict[str, float | str]] = {
    "GPT-4.1": {
        "label": "gpt-4.1",
        "price_per_1m_input_tokens": 2.00,
        "price_per_1m_output_tokens": 2.00,
    },
    "GPT-4.1 Mini": {
        "label": "gpt-4.1-mini",
        "price_per_1m_input_tokens": 0.40,
        "price_per_1m_output_tokens": 1.60,
    },
    "GPT-3.5 Turbo": {
        "label": "gpt-3.5-turbo",
        "price_per_1m_input_tokens": 0.50,
        "price_per_1m_output_tokens": 1.50,
    },
}
