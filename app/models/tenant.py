"""
Tenant model.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="basic")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # relationships
    users = relationship("User", back_populates="tenant", lazy="dynamic")
    subscriptions = relationship("Subscription", back_populates="tenant", lazy="dynamic")
    services = relationship("Service", back_populates="tenant", lazy="dynamic")
    staff_members = relationship("Staff", back_populates="tenant", lazy="dynamic")
    customers = relationship("Customer", back_populates="tenant", lazy="dynamic")
    appointments = relationship("Appointment", back_populates="tenant", lazy="dynamic")
    payments = relationship("Payment", back_populates="tenant", lazy="dynamic")
    events = relationship("Event", back_populates="tenant", lazy="dynamic")
