"""
Booking service — appointment CRUD + status state machine.
"""

from datetime import timedelta, datetime, date, timezone
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
from app.schemas.service import ServiceOut

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

VALID_APPOINTMENT_STATUSES = {
    "PENDING",
    "CONFIRMED",
    "IN_PROGRESS",
    "COMPLETED",
    "CANCELLED",
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
            if not svc:
                raise NotFoundError("Service not found")
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
        if new not in VALID_APPOINTMENT_STATUSES:
            raise BadRequestError(f"Invalid status: {new}")

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

    def assign_staff(
        self,
        appointment_id: UUID,
        tenant_id: UUID,
        staff_id: UUID,
    ) -> AppointmentOut:
        appt = self.appt_repo.get_by_id(appointment_id, tenant_id=tenant_id)
        if not appt:
            raise NotFoundError("Appointment not found")

        if appt.status in ("COMPLETED", "CANCELLED"):
            raise BadRequestError("Cannot assign staff for completed/cancelled appointment")

        staff = self.staff_repo.get_by_id(staff_id, tenant_id=tenant_id)
        if not staff or not staff.is_active:
            raise NotFoundError("Staff not found or inactive")

        appt.staff_id = staff.id
        appt = self.appt_repo.update(appt)
        return AppointmentOut.model_validate(appt)

    def get_public_service_detail(self, service_id: UUID) -> ServiceOut:
        svc = self.db.query(self.service_repo.model).filter(self.service_repo.model.id == service_id).first()
        if not svc or not svc.is_active:
            raise NotFoundError("Service not found")
        return ServiceOut.model_validate(svc)

    def get_service_availability(self, service_id: UUID, for_date: date) -> dict:
        svc = self.db.query(self.service_repo.model).filter(self.service_repo.model.id == service_id).first()
        if not svc or not svc.is_active:
            raise NotFoundError("Service not found")

        day_start = datetime.combine(for_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        appointments = self.appt_repo.list_by_day(
            tenant_id=svc.tenant_id, day_start=day_start, day_end=day_end
        )

        duration = timedelta(minutes=svc.duration_min)
        open_at = day_start.replace(hour=9, minute=0, second=0, microsecond=0)
        close_at = day_start.replace(hour=18, minute=0, second=0, microsecond=0)

        taken = {
            appt.start_at.astimezone(timezone.utc).strftime("%H:%M")
            for appt in appointments
            if appt.service_id == service_id and appt.status != "CANCELLED"
        }

        slots: list[str] = []
        cursor = open_at
        while cursor + duration <= close_at:
            key = cursor.strftime("%H:%M")
            if key not in taken:
                slots.append(key)
            cursor += duration

        staff_rows = (
            self.db.query(self.staff_repo.model)
            .filter(self.staff_repo.model.tenant_id == svc.tenant_id, self.staff_repo.model.is_active)
            .all()
        )
        staff_availability = []
        for row in staff_rows:
            busy_count = sum(
                1
                for appt in appointments
                if appt.staff_id == row.id and appt.status != "CANCELLED"
            )
            staff_availability.append(
                {"staff_id": str(row.id), "name": row.name, "booked_slots": busy_count}
            )

        return {
            "service_id": str(service_id),
            "date": str(for_date),
            "available_slots": slots,
            "staff_availability": staff_availability,
        }
