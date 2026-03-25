"""
Payment repository.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.payment import Payment
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
