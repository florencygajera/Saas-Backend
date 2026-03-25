"""
SaaS super-admin endpoints — tenant provisioning, listing, enable/disable, platform stats.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_super_admin, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.tenant import TenantCreate, TenantOut, TenantUpdate
from app.services.tenant_service import TenantService
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/saas", tags=["SaaS Admin"])


@router.post("/tenants", response_model=SingleResponse)
def provision_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_super_admin),
):
    service = TenantService(db)
    result = service.provision_tenant(payload)
    return SingleResponse(data=result.model_dump(), message="Tenant provisioned successfully")


@router.get("/tenants", response_model=PaginatedResponse)
def list_tenants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_super_admin),
):
    service = TenantService(db)
    tenants, total = service.list_tenants(skip=skip, limit=limit)
    return PaginatedResponse(
        data=[TenantOut.model_validate(t).model_dump() for t in tenants],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.patch("/tenants/{tenant_id}", response_model=SingleResponse)
def update_tenant(
    tenant_id: UUID,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_super_admin),
):
    service = TenantService(db)
    result = service.update_tenant(tenant_id, payload)
    return SingleResponse(data=result.model_dump(), message="Tenant updated")


@router.get("/platform/stats", response_model=SingleResponse)
def platform_stats(
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_super_admin),
):
    analytics = AnalyticsService(db)
    stats = analytics.get_platform_stats()
    return SingleResponse(data=stats.model_dump())


@router.get("/tenants/{tenant_id}/stats", response_model=SingleResponse)
def tenant_stats_by_super(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(require_super_admin),
):
    analytics = AnalyticsService(db)
    stats = analytics.get_tenant_stats(tenant_id)
    return SingleResponse(data=stats.model_dump())
