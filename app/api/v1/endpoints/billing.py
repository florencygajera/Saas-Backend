"""Billing endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.billing import ChangePlanRequest
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans", response_model=SingleResponse)
def get_plans(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = BillingService(db)
    return SingleResponse(data=[p.model_dump() for p in svc.get_plans()])


@router.get("/subscription", response_model=SingleResponse)
def get_subscription(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BillingService(db)
    sub = svc.get_current_subscription(tenant_id)
    return SingleResponse(data={
        "id": str(sub.id),
        "tenant_id": str(sub.tenant_id),
        "plan": sub.plan,
        "price": float(sub.price),
        "status": sub.status,
        "start_at": sub.start_at,
        "end_at": sub.end_at,
        "created_at": sub.created_at,
    })


@router.post("/subscription/change-plan", response_model=SingleResponse)
def change_plan(
    payload: ChangePlanRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BillingService(db)
    sub = svc.change_plan(tenant_id, payload.plan)
    return SingleResponse(
        data={
            "id": str(sub.id),
            "tenant_id": str(sub.tenant_id),
            "plan": sub.plan,
            "price": float(sub.price),
            "status": sub.status,
            "start_at": sub.start_at,
            "end_at": sub.end_at,
            "created_at": sub.created_at,
        },
        message="Plan updated",
    )


@router.post("/portal", response_model=SingleResponse)
def billing_portal(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BillingService(db)
    return SingleResponse(data={"url": svc.get_portal_link(tenant_id)})


@router.get("/invoices", response_model=PaginatedResponse)
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = BillingService(db)
    items, total = svc.list_invoices(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(total=total, skip=skip, limit=limit, has_more=(skip + limit < total)),
    )
