"""
Service CRUD endpoints — tenant admin only.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut
from app.services.service_service import ServiceService

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("", response_model=SingleResponse)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = ServiceService(db)
    result = svc.create(tenant_id=user.tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Service created")


@router.get("", response_model=PaginatedResponse)
def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = ServiceService(db)
    items, total = svc.list(tenant_id=user.tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[s.model_dump() for s in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.get("/{service_id}", response_model=SingleResponse)
def get_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = ServiceService(db)
    result = svc.get(service_id, tenant_id=user.tenant_id)
    return SingleResponse(data=result.model_dump())


@router.put("/{service_id}", response_model=SingleResponse)
def update_service(
    service_id: UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = ServiceService(db)
    result = svc.update(service_id, tenant_id=user.tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Service updated")


@router.delete("/{service_id}", response_model=SingleResponse)
def delete_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = ServiceService(db)
    svc.delete(service_id, tenant_id=user.tenant_id)
    return SingleResponse(message="Service deleted")
