"""
Appointment endpoints — tenant admin views + status transitions.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_tenant_admin, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.appointment import StatusUpdate, AppointmentOut
from app.services.booking_service import BookingService

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("", response_model=PaginatedResponse)
def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = BookingService(db)
    items, total = svc.list_tenant_appointments(
        tenant_id=user.tenant_id, skip=skip, limit=limit
    )
    return PaginatedResponse(
        data=[a.model_dump() for a in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.patch("/{appointment_id}/status", response_model=SingleResponse)
def update_appointment_status(
    appointment_id: UUID,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Status transition endpoint — works for both TENANT_ADMIN and CUSTOMER.
    Role + allowed transitions are validated in the service layer.
    """
    from app.repositories.customer_repo import CustomerRepository

    svc = BookingService(db)

    customer_id = None
    if user.role == "CUSTOMER":
        cust_repo = CustomerRepository(db)
        customer = cust_repo.get_by_user_id(user.user_id, user.tenant_id)
        customer_id = customer.id if customer else None

    result = svc.update_status(
        appointment_id=appointment_id,
        tenant_id=user.tenant_id,
        role=user.role,
        payload=payload,
        customer_id=customer_id,
    )
    return SingleResponse(data=result.model_dump(), message="Status updated")
