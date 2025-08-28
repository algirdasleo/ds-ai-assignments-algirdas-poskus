from datetime import datetime
from typing import List

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    doc_id: str
    title: str
    authors: List[str]
    published: datetime
    pdf_url: str


class ChunkMetadata(BaseModel):
    doc_id: str
    chunk_index: int
    content: str


class Metadata(BaseModel):
    document: DocumentMetadata
    chunks: List[ChunkMetadata] = []
