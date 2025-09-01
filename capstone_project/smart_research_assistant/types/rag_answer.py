from typing import List

from pydantic import BaseModel


class Reference(BaseModel):
    title: str | None
    quote: str
    url: str
    chunk_idx: int | None


class AnswerModel(BaseModel):
    answer: str
    references: List[Reference]
