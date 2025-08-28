from pydantic import BaseModel


class RelevantDocument(BaseModel):
    doc_id: str
    chunk_id: int
    similarity_score: float
