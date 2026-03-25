"""
Common schemas: pagination, response wrapper.
"""

from typing import Any, Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    has_more: bool


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[Any]  # typed in endpoints
    message: str = "Success"
    meta: PaginationMeta


class SingleResponse(BaseModel):
    data: Any = None
    message: str = "Success"


class MessageResponse(BaseModel):
    message: str
