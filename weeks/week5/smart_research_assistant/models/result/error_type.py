from enum import Enum


class ErrorType(Enum):
    NONE = "None"
    INVALID_API_KEY = "Invalid API Key"
    RATE_LIMIT_EXCEEDED = "Rate Limit Exceeded"
    UNHANDLED_EXCEPTION = "Unhandled Exception"
    AUTHENTICATION_ERROR = "Authentication Error"
    CONNECTION_ERROR = "Connection Error"
    BAD_REQUEST = "Bad Request"
