"""
Service schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    duration_min: int = 30
    price: float = 0.0


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    duration_min: Optional[int] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class ServiceOut(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    duration_min: int
    price: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
