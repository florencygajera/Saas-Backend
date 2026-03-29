"""Project schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    progress: int = Field(default=0, ge=0, le=100)
    members_count: int = Field(default=0, ge=0)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    members_count: Optional[int] = Field(default=None, ge=0)


class ProjectOut(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    progress: int
    members_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

