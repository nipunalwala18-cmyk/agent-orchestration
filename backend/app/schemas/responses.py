from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper schema for all endpoints."""

    success: bool
    message: str
    data: T | None = None
