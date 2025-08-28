from typing import List

from smart_research_assistant.configs.config import Settings
from smart_research_assistant.db.database import get_session
from smart_research_assistant.db.tables import DocumentMetadataSQL
from smart_research_assistant.helpers.database_helper import (
    metadata_to_sql_models,
    sql_models_to_metadata,
)
from smart_research_assistant.services.metadata_stores.base import Metadata, MetadataStore
from smart_research_assistant.types.result.result import ErrorType, Result
from sqlmodel import delete, select

# Pydantic will throw error if any required env vars are missing at runtime
settings = Settings()  # type: ignore


class SQLMetadataStore(MetadataStore):
    def upsert(self, doc_id: str, metadata: Metadata) -> Result[None]:
        try:
            with get_session() as session:
                existing_doc = session.exec(
                    select(DocumentMetadataSQL).where(DocumentMetadataSQL.doc_id == doc_id)
                ).one_or_none()
                if existing_doc:
                    session.delete(existing_doc)  # Deletes the doc with all its relationships using cascade delete

                sql_model = metadata_to_sql_models(metadata)
                session.add(sql_model)

                session.commit()

                return Result.ok(None)
        except Exception as e:
            return Result.fail(ErrorType.METADATA_STORE_ERROR, str(e))

    def get(self, doc_id: str) -> Result[Metadata]:
        try:
            with get_session() as session:
                doc = session.exec(
                    select(DocumentMetadataSQL).where(DocumentMetadataSQL.doc_id == doc_id)
                ).one_or_none()
                if not doc:
                    return Result.fail(ErrorType.METADATA_STORE_ERROR, "Missing document metadata")
                return Result.ok(sql_models_to_metadata(doc))
        except Exception as e:
            return Result.fail(ErrorType.METADATA_STORE_ERROR, str(e))

    def get_document_ids(self) -> Result[List[str]]:
        try:
            with get_session() as session:
                ids = session.exec(select(DocumentMetadataSQL.doc_id)).all()
                return Result.ok(ids)
        except Exception as e:
            return Result.fail(ErrorType.METADATA_STORE_ERROR, str(e))

    def clear(self) -> Result[None]:
        try:
            with get_session() as session:
                session.exec(delete(DocumentMetadataSQL))  # type: ignore
                session.commit()
                return Result.ok(None)
        except Exception as e:
            return Result.fail(ErrorType.METADATA_STORE_ERROR, str(e))

    def close(self) -> Result[None]:
        return Result.ok(None)
