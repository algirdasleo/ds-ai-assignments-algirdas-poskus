from io import BytesIO
from typing import Dict, List

import pdfplumber
import requests
import tiktoken
from smart_research_assistant.types.metadata import DocumentMetadata, Metadata
from smart_research_assistant.types.rag_answer import AnswerModel
from streamlit.delta_generator import DeltaGenerator
from transformers import GPT2Tokenizer


def remove_text_references(pages: List[str]) -> str:
    keywords = ["references", "bibliography", "works cited"]

    for i in reversed(range(len(pages))):
        lines = pages[i].splitlines()

        for line in reversed(lines):
            if line.strip().lower() in keywords:
                pages_before = pages[:i]
                lines_before = lines[: lines.index(line)]
                return "\n".join(pages_before + lines_before)

    return "\n".join(pages)


def extract_text_from_pdf(metadata: DocumentMetadata) -> str:
    response = requests.get(metadata.pdf_url, stream=True)
    if response.status_code != 200:
        raise ValueError(f"Failed to download PDF: {metadata.pdf_url}. Error: {response.text}")

    pdf_stream = BytesIO(response.content)

    with pdfplumber.open(pdf_stream) as pdf:
        pages = [page.extract_text() for page in pdf.pages if page.extract_text()]

        text_without_references = remove_text_references(pages)

    return text_without_references


def format_messages(
    user_prompt: str | None = None,
    system_prompt: str | None = None,
    history: List[Dict[str, str]] | None = None,
) -> List:

    messages = []

    if history:
        if history[0]["role"] != "system":
            messages.append({"role": "system", "content": system_prompt or "You are a helpful assistant."})
        elif history[0]["role"] == "system" and system_prompt:
            history[0]["content"] = system_prompt

        messages.extend(history)
    else:
        messages.append({"role": "system", "content": system_prompt or "You are a helpful assistant."})

    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    return messages


def form_context(metadata: List[Metadata], web_search_data: List[Dict[str, str]]) -> str:
    context = ""
    for item in metadata:
        context += (
            f'[TITLE: "{item.document.title}", '
            f'LINK: "{item.document.pdf_url}", '
            f"CHUNK NO. {item.chunks[0].chunk_index}]\n\n"
            f'CONTENT: "{item.chunks[0].content}"\n\n\n'
        )

    context += "[WEB SEARCH RESULTS]:\n\n"
    for item in web_search_data:
        for key, value in item.items():
            context += f"{key}: {value}\n\n"

    return context


def write_references(answer_model: AnswerModel, stream_box: DeltaGenerator | None):
    if not stream_box:
        return

    references = ""
    for i, reference in enumerate(answer_model.references):
        references += (
            f'{i + 1}. Citation: "{reference.quote}".\n\n'
            f':green-badge[ Document Title: "{reference.title or 'N/A'}" ]'
            f":green-badge[ URL: {reference.url or 'N/A'} ]"
        )
        if reference.chunk_idx:
            references += f":green-badge[ Chunk Index: {reference.chunk_idx} ]"
        references += "\n\n"

    stream_box.write(references)


tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


def count_tokens(text: str, model_name: str) -> int:
    if not text:
        return 0

    try:
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))

    except Exception as _:
        pass  # Fallback to GPT-2 tokenizer

    try:
        max_chunk_length = 1024  # Max size for GPT-2

        split_text = text.split()
        if len(split_text) > max_chunk_length:
            total_tokens = 0

            for i in range(0, len(split_text), max_chunk_length):
                chunk_words = split_text[i : i + max_chunk_length]
                chunk_text = " ".join(chunk_words)
                chunk_tokens = tokenizer.encode(chunk_text)
                total_tokens += len(chunk_tokens)

            return total_tokens
        else:
            return len(tokenizer.encode(text))

    except Exception as _:
        # If even GPT-2 tokenizer fails, then fallback to word count
        return len(text.split()) * 2
