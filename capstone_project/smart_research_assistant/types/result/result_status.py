from enum import Enum


class ResultStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"

    def __str__(self) -> str:
        return self.value
