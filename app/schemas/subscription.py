"""
Subscription schemas (standalone).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    plan: str = "basic"
    price: float = 29.99
    status: str = "active"
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class SubscriptionOut(BaseModel):
    id: UUID
    tenant_id: UUID
    plan: str
    price: float
    status: str
    start_at: datetime
    end_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
