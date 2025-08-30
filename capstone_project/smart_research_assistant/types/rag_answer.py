from typing import List

from pydantic import BaseModel


class Reference(BaseModel):
    title: str
    pdf_url: str
    chunk_idx: int | None
    quote: str


class AnswerModel(BaseModel):
    answer: str
    references: List[Reference]
