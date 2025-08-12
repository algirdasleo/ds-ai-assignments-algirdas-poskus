from typing import List

from openai.types.chat import ChatCompletionMessageParam


def form_messages(
    user_prompt: str | None = None,
    system_prompt: str | None = None,
    history: List[ChatCompletionMessageParam] | None = None,
) -> List[ChatCompletionMessageParam]:

    messages: List[ChatCompletionMessageParam] = []

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
