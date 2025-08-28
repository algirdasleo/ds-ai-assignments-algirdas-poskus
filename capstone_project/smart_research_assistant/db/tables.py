from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel


class DocumentMetadataSQL(SQLModel, table=True):
    __tablename__ = "documents"  # type:ignore
    __table_args__ = {"extend_existing": True}

    doc_id: str = Field(primary_key=True)
    title: str
    published: datetime
    pdf_url: str

    authors: List["smart_research_assistant.db.tables.AuthorSQL"] = Relationship(
        back_populates="document", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    chunks: List["smart_research_assistant.db.tables.ChunkMetadataSQL"] = Relationship(
        back_populates="document", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class AuthorSQL(SQLModel, table=True):
    __tablename__ = "authors"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    doc_id: str = Field(foreign_key="documents.doc_id", ondelete="CASCADE")
    name: str

    document: Optional["smart_research_assistant.db.tables.DocumentMetadataSQL"] = Relationship(
        back_populates="authors"
    )


class ChunkMetadataSQL(SQLModel, table=True):
    __tablename__ = "chunks"  # type:ignore
    __table_args__ = {"extend_existing": True}

    doc_id: str = Field(foreign_key="documents.doc_id", primary_key=True)
    chunk_index: int = Field(primary_key=True)
    content: str

    document: Optional["smart_research_assistant.db.tables.DocumentMetadataSQL"] = Relationship(back_populates="chunks")


if TYPE_CHECKING:
    DocumentMetadataSQL.model_rebuild()
    AuthorSQL.model_rebuild()
    ChunkMetadataSQL.model_rebuild()
