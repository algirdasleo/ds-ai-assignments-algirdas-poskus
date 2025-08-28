from enum import StrEnum


class ErrorType(StrEnum):
    NONE = "none"
    INVALID_API_KEY = "invalid_api_key"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNHANDLED_EXCEPTION = "unhandled_exception"
    AUTHENTICATION_ERROR = "authentication_error"
    CONNECTION_ERROR = "connection_error"
    BAD_REQUEST = "bad_request"
    VECTOR_STORE_ERROR = "vector_store_error"
    METADATA_STORE_ERROR = "metadata_store_error"
    EMBEDDING_ERROR = "embedding_error"
    RAG_PIPELINE_ERROR = "rag_pipeline_error"
    NO_SIMILAR_DOCUMENTS_FOUND = "no_similar_documents_found"
    EMPTY_RESULT = "empty_result"
    MODEL_REFUSED = "model_refused"
    INVALID_PARAMETERS = "invalid_parameters"
    ARXIV_ERROR = "arxiv_error"
