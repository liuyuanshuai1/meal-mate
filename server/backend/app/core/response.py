from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int
    data: T | None
    message: str


class AppException(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def ok(data: Any = None, message: str = "") -> dict[str, Any]:
    return {"code": 0, "data": data if data is not None else {}, "message": message}


def fail(code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {"code": code, "data": data if data is not None else {}, "message": message}
