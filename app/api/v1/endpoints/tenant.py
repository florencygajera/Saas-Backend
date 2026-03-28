"""Tenant admin endpoints: services, staff, customers, appointments, analytics."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.staff import StaffCreate, StaffUpdate
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.appointment import StatusUpdate, AssignStaffRequest
from app.services.service_service import ServiceService
from app.services.staff_service import StaffService
from app.services.customer_service import CustomerService
from app.services.booking_service import BookingService
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Tenant Admin"])


@router.post("/services", response_model=SingleResponse)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ServiceService(db)
    result = svc.create(tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Service created")


@router.get("/services", response_model=PaginatedResponse)
def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ServiceService(db)
    items, total = svc.list(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.get("/services/{service_id}", response_model=SingleResponse)
def get_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ServiceService(db)
    result = svc.get(service_id, tenant_id=tenant_id)
    return SingleResponse(data=result.model_dump())


@router.put("/services/{service_id}", response_model=SingleResponse)
def update_service(
    service_id: UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ServiceService(db)
    result = svc.update(service_id, tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Service updated")


@router.delete("/services/{service_id}", response_model=SingleResponse)
def delete_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ServiceService(db)
    svc.delete(service_id, tenant_id=tenant_id)
    return SingleResponse(message="Service deleted")


@router.post("/staff", response_model=SingleResponse)
def create_staff(
    payload: StaffCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = StaffService(db)
    result = svc.create(tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Staff created")


@router.get("/staff", response_model=PaginatedResponse)
def list_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = StaffService(db)
    items, total = svc.list(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.get("/staff/{staff_id}", response_model=SingleResponse)
def get_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = StaffService(db)
    result = svc.get(staff_id, tenant_id=tenant_id)
    return SingleResponse(data=result.model_dump())


@router.put("/staff/{staff_id}", response_model=SingleResponse)
def update_staff(
    staff_id: UUID,
    payload: StaffUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = StaffService(db)
    result = svc.update(staff_id, tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Staff updated")


@router.delete("/staff/{staff_id}", response_model=SingleResponse)
def delete_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = StaffService(db)
    svc.delete(staff_id, tenant_id=tenant_id)
    return SingleResponse(message="Staff deleted")


@router.post("/customers", response_model=SingleResponse)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = CustomerService(db)
    result = svc.create(tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Customer created")


@router.get("/customers", response_model=PaginatedResponse)
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = CustomerService(db)
    items, total = svc.list(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.get("/customers/{customer_id}", response_model=SingleResponse)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = CustomerService(db)
    result = svc.get(customer_id, tenant_id=tenant_id)
    return SingleResponse(data=result.model_dump())


@router.put("/customers/{customer_id}", response_model=SingleResponse)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = CustomerService(db)
    result = svc.update(customer_id, tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Customer updated")


@router.delete("/customers/{customer_id}", response_model=SingleResponse)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = CustomerService(db)
    svc.delete(customer_id, tenant_id=tenant_id)
    return SingleResponse(message="Customer deleted")


@router.get("/appointments", response_model=PaginatedResponse)
def list_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    items, total = svc.list_tenant_appointments(
        tenant_id=tenant_id, skip=skip, limit=limit
    )
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.patch("/appointments/{appointment_id}/status", response_model=SingleResponse)
def update_appointment_status(
    appointment_id: UUID,
    payload: StatusUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    result = svc.update_status(
        appointment_id=appointment_id,
        tenant_id=tenant_id,
        role=user.role,
        payload=payload,
    )
    return SingleResponse(data=result.model_dump(), message="Status updated")


@router.patch(
    "/appointments/{appointment_id}/assign-staff",
    response_model=SingleResponse,
)
def assign_appointment_staff(
    appointment_id: UUID,
    payload: AssignStaffRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BookingService(db)
    result = svc.assign_staff(
        appointment_id=appointment_id, tenant_id=tenant_id, staff_id=payload.staff_id
    )
    return SingleResponse(data=result.model_dump(), message="Staff assigned")


@router.get("/tenant/stats", response_model=SingleResponse)
def tenant_stats(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    analytics = AnalyticsService(db)
    stats = analytics.get_tenant_stats(tenant_id)
    return SingleResponse(data=stats.model_dump())
