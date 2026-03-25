"""
Appointment schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    service_id: UUID
    staff_id: Optional[UUID] = None
    start_at: datetime
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    """For rescheduling — only allowed when status is PENDING."""

    start_at: Optional[datetime] = None
    notes: Optional[str] = None


class StatusUpdate(BaseModel):
    new_status: str


class AppointmentOut(BaseModel):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    staff_id: Optional[UUID] = None
    service_id: UUID
    start_at: datetime
    end_at: datetime
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
