"""Customer booking endpoints - browse services and manage own bookings."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import (
    require_customer,
    CurrentUser,
    get_optional_current_user,
    require_tenant_scope,
)
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.booking_service import BookingService
from app.services.service_service import ServiceService
from app.repositories.customer_repo import CustomerRepository

router = APIRouter(tags=["Bookings"])


def _get_customer_id(user: CurrentUser, db: Session) -> UUID:
    tenant_id = require_tenant_scope(user)
    repo = CustomerRepository(db)
    customer = repo.get_by_user_id(user.user_id, tenant_id)
    if not customer:
        raise NotFoundError(
            "No customer profile linked to your account. Contact the business admin."
        )
    return customer.id


@router.get("/public/services", response_model=PaginatedResponse)
def browse_services(
    tenant_id: UUID | None = Query(
        default=None,
        description="Tenant ID to browse services for",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: CurrentUser | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    scoped_tenant_id = tenant_id
    if scoped_tenant_id is None and user and user.tenant_id:
        scoped_tenant_id = user.tenant_id
    if scoped_tenant_id is None:
        raise BadRequestError("tenant_id is required when unauthenticated")

    svc = ServiceService(db)
    items, _ = svc.list(tenant_id=scoped_tenant_id, skip=skip, limit=limit)
    active = [s for s in items if s.is_active]

    return PaginatedResponse(
        data=[s.model_dump() for s in active],
        meta=PaginationMeta(total=len(active), skip=skip, limit=limit, has_more=False),
    )


@router.post("/bookings", response_model=SingleResponse)
def create_booking(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_customer),
):
    customer_id = _get_customer_id(user, db)
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    result = svc.create_appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        payload=payload,
    )
    return SingleResponse(data=result.model_dump(), message="Booking created")


@router.get("/bookings/my", response_model=PaginatedResponse)
def my_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_customer),
):
    customer_id = _get_customer_id(user, db)
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    items, total = svc.list_customer_bookings(
        customer_id=customer_id,
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
    )
    return PaginatedResponse(
        data=[a.model_dump() for a in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.patch("/bookings/{booking_id}", response_model=SingleResponse)
def reschedule_booking(
    booking_id: UUID,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_customer),
):
    customer_id = _get_customer_id(user, db)
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    result = svc.reschedule(
        appointment_id=booking_id,
        tenant_id=tenant_id,
        customer_id=customer_id,
        payload=payload,
    )
    return SingleResponse(data=result.model_dump(), message="Booking rescheduled")


@router.delete("/bookings/{booking_id}", response_model=SingleResponse)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_customer),
):
    customer_id = _get_customer_id(user, db)
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    result = svc.cancel_by_customer(
        appointment_id=booking_id,
        tenant_id=tenant_id,
        customer_id=customer_id,
    )
    return SingleResponse(data=result.model_dump(), message="Booking cancelled")
