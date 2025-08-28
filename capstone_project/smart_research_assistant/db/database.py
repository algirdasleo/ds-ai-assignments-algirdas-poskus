from smart_research_assistant.configs.config import Settings
from smart_research_assistant.db.tables import (  # They need to be imported here, for init_db.py to work as intended
    AuthorSQL,
    ChunkMetadataSQL,
    DocumentMetadataSQL,
)
from smart_research_assistant.types.result.error_type import ErrorType
from smart_research_assistant.types.result.result import Result
from sqlmodel import Session, SQLModel, create_engine

# Pydantic will throw error if any required env vars are missing at runtime
settings = Settings()  # type: ignore

try:
    engine = create_engine(settings.connection_string)
except Exception as e:
    raise RuntimeError(f"Failed to connect to the database: {e}")


def create_tables() -> Result[None]:
    # To further improve this, I would have added a migration tool like Alembic to manage migrations,
    # So that schemas can be updated without losing data.
    try:
        SQLModel.metadata.create_all(engine)
        return Result.ok(None)
    except Exception as e:
        return Result.fail(ErrorType.METADATA_STORE_ERROR, f"Failed to create tables: {e}")


def get_session() -> Session:
    return Session(engine)
