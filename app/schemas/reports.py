"""Reports schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionRow(BaseModel):
    payment_id: UUID
    appointment_id: UUID
    customer_name: str
    service_name: str
    amount: float
    currency: str
    status: str
    date: datetime

