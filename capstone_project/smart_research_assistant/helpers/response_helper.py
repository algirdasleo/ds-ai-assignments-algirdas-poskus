from openai.types.chat import ChatCompletionChunk
from transformers import GPT2Tokenizer

_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


def extract_chunk_text(chunk: ChatCompletionChunk) -> str:
    if not chunk.choices or not chunk.choices[0].delta or not chunk.choices[0].delta.content:
        return ""
    return chunk.choices[0].delta.content


def count_tokens(text: str) -> int:
    tokens = _tokenizer.encode(text)
    return len(tokens)
