"""Payment repository."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.customer import Customer
from app.models.service import Service
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_appointment(
        self, appointment_id: UUID, tenant_id: UUID
    ) -> Optional[Payment]:
        return (
            self.db.query(Payment)
            .filter(
                Payment.appointment_id == appointment_id,
                Payment.tenant_id == tenant_id,
            )
            .order_by(Payment.created_at.desc())
            .first()
        )

    def list_transactions(
        self,
        tenant_id: UUID,
        status: str | None = None,
        search: str | None = None,
        from_dt: datetime | None = None,
        to_dt: datetime | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[tuple], int]:
        q = (
            self.db.query(Payment, Appointment, Customer, Service)
            .join(Appointment, Payment.appointment_id == Appointment.id)
            .join(Customer, Appointment.customer_id == Customer.id)
            .join(Service, Appointment.service_id == Service.id)
            .filter(Payment.tenant_id == tenant_id)
        )
        if status:
            q = q.filter(Payment.status == status.upper())
        if search:
            s = f"%{search.strip()}%"
            q = q.filter(or_(Customer.name.ilike(s), Service.name.ilike(s)))
        if from_dt:
            q = q.filter(Payment.created_at >= from_dt)
        if to_dt:
            q = q.filter(Payment.created_at <= to_dt)

        total = q.count()
        rows = (
            q.order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return rows, total
