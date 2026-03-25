"""
Staff CRUD endpoints — tenant admin only.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.staff import StaffCreate, StaffUpdate
from app.services.staff_service import StaffService

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.post("", response_model=SingleResponse)
def create_staff(
    payload: StaffCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = StaffService(db)
    result = svc.create(tenant_id=user.tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Staff created")


@router.get("", response_model=PaginatedResponse)
def list_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = StaffService(db)
    items, total = svc.list(tenant_id=user.tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[s.model_dump() for s in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.get("/{staff_id}", response_model=SingleResponse)
def get_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = StaffService(db)
    result = svc.get(staff_id, tenant_id=user.tenant_id)
    return SingleResponse(data=result.model_dump())


@router.put("/{staff_id}", response_model=SingleResponse)
def update_staff(
    staff_id: UUID,
    payload: StaffUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = StaffService(db)
    result = svc.update(staff_id, tenant_id=user.tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Staff updated")


@router.delete("/{staff_id}", response_model=SingleResponse)
def delete_staff(
    staff_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = StaffService(db)
    svc.delete(staff_id, tenant_id=user.tenant_id)
    return SingleResponse(message="Staff deleted")
