from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from smart_research_assistant.models.result.error_type import ErrorType
from smart_research_assistant.models.result.result_status import ResultStatus

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    status: ResultStatus
    data: T | None
    error: ErrorType
    error_message: str | None = None

    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS

    @classmethod
    def ok(cls, data: T) -> Result[T]:
        return cls(data=data, error=ErrorType.NONE, status=ResultStatus.SUCCESS)

    @classmethod
    def fail(cls, error: ErrorType, error_message: str | None) -> Result[Any]:
        return cls(data=None, error=error, status=ResultStatus.FAILURE, error_message=error_message)
