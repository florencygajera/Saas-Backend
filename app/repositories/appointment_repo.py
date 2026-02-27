"""
Appointment repository.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self, db: Session):
        super().__init__(Appointment, db)

    def get_by_customer(
        self,
        customer_id: UUID,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Appointment]:
        return (
            self.db.query(Appointment)
            .filter(
                Appointment.tenant_id == tenant_id,
                Appointment.customer_id == customer_id,
            )
            .order_by(Appointment.start_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_customer(self, customer_id: UUID, tenant_id: UUID) -> int:
        return (
            self.db.query(Appointment)
            .filter(
                Appointment.tenant_id == tenant_id,
                Appointment.customer_id == customer_id,
            )
            .count()
        )
