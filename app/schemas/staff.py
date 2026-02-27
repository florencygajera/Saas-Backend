"""
Staff schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StaffCreate(BaseModel):
    name: str


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class StaffOut(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
