from typing import Dict, List

from pydantic import BaseModel


class ResponseDetails(BaseModel):
    response: str
    parsed_response: BaseModel | None = None
    tokens_used: int
    time_to_first_token: float
    total_time: float
    model_name: str
    updated_messages: List[Dict[str, str]]
