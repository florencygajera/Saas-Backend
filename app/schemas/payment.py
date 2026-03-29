"""
Payment schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentStartRequest(BaseModel):
    appointment_id: UUID


class PaymentVerifyRequest(BaseModel):
    payment_id: UUID
    otp: str  # any 4-digit string accepted
    model_config = ConfigDict(extra="forbid")


class PaymentOut(BaseModel):
    id: UUID
    tenant_id: UUID
    appointment_id: UUID
    amount: float
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentReceipt(BaseModel):
    payment_id: UUID
    appointment_id: UUID
    amount: float
    currency: str
    status: str
    paid_at: datetime
    message: str = "Payment verified successfully"
