"""
Payment service — simulated payment start + OTP verify flow.
"""

import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, BadRequestError
from app.models.payment import Payment
from app.repositories.payment_repo import PaymentRepository
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.service_repo import ServiceRepository
from app.schemas.payment import PaymentOut, PaymentReceipt


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.appt_repo = AppointmentRepository(db)
        self.service_repo = ServiceRepository(db)

    def start_payment(self, appointment_id: UUID, tenant_id: UUID) -> PaymentOut:
        appt = self.appt_repo.get_by_id(appointment_id, tenant_id=tenant_id)
        if not appt:
            raise NotFoundError("Appointment not found")

        # Get service price
        svc = self.service_repo.get_by_id(appt.service_id, tenant_id=tenant_id)
        if not svc:
            raise NotFoundError("Service not found")

        # Check for existing non-failed payment
        existing = self.payment_repo.get_by_appointment(appointment_id, tenant_id)
        if existing and existing.status in ("PROCESSING", "PAID"):
            raise BadRequestError(
                f"Payment already exists with status {existing.status}"
            )

        payment = Payment(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            amount=float(svc.price),
            currency="USD",
            status="PROCESSING",
        )
        payment = self.payment_repo.create(payment)
        return PaymentOut.model_validate(payment)

    def verify_payment(
        self, payment_id: UUID, otp: str, tenant_id: UUID
    ) -> PaymentReceipt:
        # Validate OTP format — any 4-digit string
        if not re.match(r"^\d{4}$", otp):
            raise BadRequestError("OTP must be a 4-digit number")

        payment = self.payment_repo.get_by_id(payment_id, tenant_id=tenant_id)
        if not payment:
            raise NotFoundError("Payment not found")
        if payment.status != "PROCESSING":
            raise BadRequestError(f"Payment status is {payment.status}, expected PROCESSING")

        # Mark paid
        payment.status = "PAID"
        self.db.commit()
        self.db.refresh(payment)

        # Auto-confirm appointment if PENDING
        appt = self.appt_repo.get_by_id(payment.appointment_id, tenant_id=tenant_id)
        if appt and appt.status == "PENDING":
            appt.status = "CONFIRMED"
            self.db.commit()

        return PaymentReceipt(
            payment_id=payment.id,
            appointment_id=payment.appointment_id,
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            paid_at=datetime.now(timezone.utc),
        )
