"""Billing schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PlanOut(BaseModel):
    code: str
    name: str
    price: float
    interval: str = "monthly"
    features: list[str]


class ChangePlanRequest(BaseModel):
    plan: str = Field(..., min_length=1)


class BillingPortalOut(BaseModel):
    url: str


class InvoiceItem(BaseModel):
    payment_id: UUID
    appointment_id: UUID
    amount: float
    currency: str
    status: str
    created_at: datetime
    customer_name: Optional[str] = None

