from enum import StrEnum


class ErrorType(StrEnum):
    NONE = "none"
    INVALID_API_KEY = "invalid_api_key"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNHANDLED_EXCEPTION = "unhandled_exception"
    AUTHENTICATION_ERROR = "authentication_error"
    CONNECTION_ERROR = "connection_error"
    BAD_REQUEST = "bad_request"
