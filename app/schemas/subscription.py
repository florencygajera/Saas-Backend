"""
Subscription schemas (standalone).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    plan: str = "basic"
    price: float = 29.99
    status: str = "active"


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None


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
