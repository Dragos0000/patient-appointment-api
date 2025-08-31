from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

DataType = TypeVar('DataType')


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_next: bool = Field(..., description="Whether there are more items")


class APIResponse(BaseModel, Generic[DataType]):
    """Generic API response wrapper."""
    data: DataType = Field(..., description="Response data")
    message: str = Field(default="Success", description="Response message")


class APIListResponse(BaseModel, Generic[DataType]):
    """API response for list endpoints with pagination."""
    data: List[DataType] = Field(..., description="List of items")
    pagination: Optional[PaginationInfo] = Field(None, description="Pagination information")
    message: str = Field(default="Success", description="Response message")


class APIError(BaseModel):
    """API error response."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details")


class APIErrorResponse(BaseModel):
    """API error response wrapper."""
    error: APIError = Field(..., description="Error information")
