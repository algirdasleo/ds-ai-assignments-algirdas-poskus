from smart_research_assistant.db.tables import (
    AuthorSQL,
    ChunkMetadataSQL,
    DocumentMetadataSQL,
)
from smart_research_assistant.types.metadata import ChunkMetadata, DocumentMetadata, Metadata


def metadata_to_sql_models(metadata: Metadata) -> DocumentMetadataSQL:
    return DocumentMetadataSQL(
        doc_id=metadata.document.doc_id,
        title=metadata.document.title,
        published=metadata.document.published,
        pdf_url=metadata.document.pdf_url,
        authors=[AuthorSQL(name=a, doc_id=metadata.document.doc_id) for a in metadata.document.authors],
        chunks=[
            ChunkMetadataSQL(doc_id=chunk.doc_id, chunk_index=chunk.chunk_index, content=chunk.content)
            for chunk in metadata.chunks
        ],
    )


def sql_models_to_metadata(doc: DocumentMetadataSQL) -> Metadata:
    return Metadata(
        document=DocumentMetadata(
            doc_id=doc.doc_id,
            title=doc.title,
            published=doc.published,
            pdf_url=doc.pdf_url,
            authors=[author.name for author in doc.authors],
        ),
        chunks=[
            ChunkMetadata(doc_id=chunk.doc_id, chunk_index=chunk.chunk_index, content=chunk.content)
            for chunk in doc.chunks
        ],
    )
