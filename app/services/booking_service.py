"""
Booking service — appointment CRUD + status state machine.
"""

from datetime import timedelta
from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError
from app.models.appointment import Appointment
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.service_repo import ServiceRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.staff_repo import StaffRepository
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentOut,
    StatusUpdate,
)

# ---------------------------------------------------------------------------
# State machine transition rules
# ---------------------------------------------------------------------------

TENANT_ADMIN_TRANSITIONS = {
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["COMPLETED"],
    "COMPLETED": [],
    "CANCELLED": [],
}

CUSTOMER_TRANSITIONS = {
    "PENDING": ["CANCELLED"],
    # customer cannot change any other status
}


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.appt_repo = AppointmentRepository(db)
        self.service_repo = ServiceRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.staff_repo = StaffRepository(db)

    # ----- Create (customer) -----
    def create_appointment(
        self,
        tenant_id: UUID,
        customer_id: UUID,
        payload: AppointmentCreate,
    ) -> AppointmentOut:
        # Validate service exists in same tenant
        svc = self.service_repo.get_by_id(payload.service_id, tenant_id=tenant_id)
        if not svc or not svc.is_active:
            raise NotFoundError("Service not found or inactive")

        # Validate staff if provided
        if payload.staff_id:
            staff = self.staff_repo.get_by_id(payload.staff_id, tenant_id=tenant_id)
            if not staff or not staff.is_active:
                raise NotFoundError("Staff not found or inactive")

        end_at = payload.start_at + timedelta(minutes=svc.duration_min)

        appt = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=payload.staff_id,
            service_id=payload.service_id,
            start_at=payload.start_at,
            end_at=end_at,
            status="PENDING",
            notes=payload.notes,
        )
        appt = self.appt_repo.create(appt)
        return AppointmentOut.model_validate(appt)

    # ----- List tenant appointments (tenant_admin) -----
    def list_tenant_appointments(
        self, tenant_id: UUID, skip: int = 0, limit: int = 50
    ) -> Tuple[List[AppointmentOut], int]:
        items = self.appt_repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.appt_repo.count(tenant_id=tenant_id)
        return [AppointmentOut.model_validate(a) for a in items], total

    # ----- List customer bookings -----
    def list_customer_bookings(
        self,
        customer_id: UUID,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AppointmentOut], int]:
        items = self.appt_repo.get_by_customer(
            customer_id=customer_id, tenant_id=tenant_id, skip=skip, limit=limit
        )
        total = self.appt_repo.count_by_customer(
            customer_id=customer_id, tenant_id=tenant_id
        )
        return [AppointmentOut.model_validate(a) for a in items], total

    # ----- Reschedule (customer, only if PENDING) -----
    def reschedule(
        self,
        appointment_id: UUID,
        tenant_id: UUID,
        customer_id: UUID,
        payload: AppointmentUpdate,
    ) -> AppointmentOut:
        appt = self.appt_repo.get_by_id(appointment_id, tenant_id=tenant_id)
        if not appt:
            raise NotFoundError("Appointment not found")
        if appt.customer_id != customer_id:
            raise ForbiddenError("Not your appointment")
        if appt.status != "PENDING":
            raise BadRequestError("Can only reschedule PENDING appointments")

        if payload.start_at is not None:
            svc = self.service_repo.get_by_id(appt.service_id, tenant_id=tenant_id)
            appt.start_at = payload.start_at
            appt.end_at = payload.start_at + timedelta(minutes=svc.duration_min)
        if payload.notes is not None:
            appt.notes = payload.notes

        appt = self.appt_repo.update(appt)
        return AppointmentOut.model_validate(appt)

    # ----- Cancel (customer, only if PENDING) -----
    def cancel_by_customer(
        self, appointment_id: UUID, tenant_id: UUID, customer_id: UUID
    ) -> AppointmentOut:
        appt = self.appt_repo.get_by_id(appointment_id, tenant_id=tenant_id)
        if not appt:
            raise NotFoundError("Appointment not found")
        if appt.customer_id != customer_id:
            raise ForbiddenError("Not your appointment")
        if appt.status != "PENDING":
            raise BadRequestError("Can only cancel PENDING appointments")

        appt.status = "CANCELLED"
        appt = self.appt_repo.update(appt)
        return AppointmentOut.model_validate(appt)

    # ----- Status transition (tenant_admin or customer) -----
    def update_status(
        self,
        appointment_id: UUID,
        tenant_id: UUID,
        role: str,
        payload: StatusUpdate,
        customer_id: UUID | None = None,
    ) -> AppointmentOut:
        appt = self.appt_repo.get_by_id(appointment_id, tenant_id=tenant_id)
        if not appt:
            raise NotFoundError("Appointment not found")

        current = appt.status
        new = payload.new_status.upper()

        if role == "CUSTOMER":
            if customer_id and appt.customer_id != customer_id:
                raise ForbiddenError("Not your appointment")
            allowed = CUSTOMER_TRANSITIONS.get(current, [])
        elif role == "TENANT_ADMIN":
            allowed = TENANT_ADMIN_TRANSITIONS.get(current, [])
        else:
            raise ForbiddenError("Role not allowed to update status")

        if new not in allowed:
            raise BadRequestError(
                f"Cannot transition from {current} to {new}. " f"Allowed: {allowed}"
            )

        appt.status = new
        appt = self.appt_repo.update(appt)
        return AppointmentOut.model_validate(appt)
