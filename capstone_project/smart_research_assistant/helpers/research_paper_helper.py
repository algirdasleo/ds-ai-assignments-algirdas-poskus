from typing import Callable, List

import arxiv
from smart_research_assistant.services.metadata_stores.base import MetadataStore
from smart_research_assistant.types.metadata import DocumentMetadata
from smart_research_assistant.types.result.result import ErrorType, Result


def search_arxiv(query: str, n_results: int, excluded_ids: List[str]) -> Result[List[DocumentMetadata]]:
    try:
        search = arxiv.Search(
            query=query, max_results=n_results + len(excluded_ids)
        )  # Overfetch and then exclude already present IDs

        results = []
        for result in search.results():
            if result.entry_id.split("/")[-1] in excluded_ids:
                continue

            metadata = DocumentMetadata(
                doc_id=result.entry_id.split("/")[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                published=result.published,
                pdf_url=result.pdf_url or "https://arxiv.org/pdf/" + result.entry_id.split("/")[-1],
            )
            results.append(metadata)

            if len(results) >= n_results:
                break

        return Result.ok(results)

    except Exception as e:
        return Result.fail(ErrorType.ARXIV_ERROR, str(e))


def gather_documents_by_query(
    metadata_store: MetadataStore, search_query: str, n_documents: int
) -> Result[List[DocumentMetadata]]:
    try:
        existing_doc_ids_result = metadata_store.get_document_ids()
        if existing_doc_ids_result.is_success():
            existing_doc_ids = existing_doc_ids_result.data or []
        else:
            existing_doc_ids = []

        search_result = search_arxiv(query=search_query, n_results=n_documents, excluded_ids=existing_doc_ids)
        if not search_result.is_success():
            return Result.fail(ErrorType.RAG_PIPELINE_ERROR, search_result.error_message)

        return Result.ok(search_result.data)
    except Exception as e:
        return Result.fail(ErrorType.RAG_PIPELINE_ERROR, str(e))


def gather_documents_by_arxiv_ids(
    metadata_store: MetadataStore, ids: List[str], update_status: Callable[[str], None] | None
) -> Result[List[DocumentMetadata]]:
    try:
        if not ids:
            return Result.ok([])

        existing_ids_result = metadata_store.get_document_ids()
        existing_ids = existing_ids_result.data if existing_ids_result.is_success() and existing_ids_result.data else []

        # Skip duplicates
        remaining_ids = []
        for id in ids:
            if id in existing_ids:
                send_status_update(f"Document {id} is already ingested.", update_status)
                continue
            remaining_ids.append(id)

        if not remaining_ids:
            return Result.ok([])

        # Fetch metadata for remaining IDs
        search = arxiv.Search(id_list=remaining_ids)
        results: List[DocumentMetadata] = []
        for result in search.results():
            doc_id = result.entry_id.split("/")[-1]
            if doc_id in existing_ids:
                continue
            metadata = DocumentMetadata(
                doc_id=doc_id,
                title=result.title,
                authors=[a.name for a in result.authors],
                published=result.published,
                pdf_url=result.pdf_url or ("https://arxiv.org/pdf/" + doc_id),
            )
            results.append(metadata)

        return Result.ok(results)
    except Exception as e:
        return Result.fail(ErrorType.ARXIV_ERROR, str(e))


def send_status_update(message: str, update_status: Callable[[str], None] | None = None):
    if update_status:
        update_status(message)
