"""API key schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApiKeyCreateRequest(BaseModel):
    name: str


class ApiKeyOut(BaseModel):
    id: UUID
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApiKeyCreateResponse(ApiKeyOut):
    api_key: str

