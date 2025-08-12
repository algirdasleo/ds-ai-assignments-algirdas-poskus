from pydantic import BaseModel


class ResultDetails(BaseModel):
    response: str | None
    tokens_used: int | None
    total_time: float | None
    model_name: str | None
