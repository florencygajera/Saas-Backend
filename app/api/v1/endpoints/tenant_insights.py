"""Tenant analytics and reports endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.services.analytics_service import AnalyticsService
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/tenant", tags=["Tenant Insights"])


@router.get("/analytics", response_model=SingleResponse)
def tenant_analytics(
    range: str = Query(default="7d"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = AnalyticsService(db)
    data = svc.get_tenant_analytics(tenant_id=tenant_id, range_key=range)
    return SingleResponse(data=data.model_dump())


@router.get("/stats/trend", response_model=SingleResponse)
def tenant_trend(
    range: str = Query(default="7d"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = AnalyticsService(db)
    data = svc.get_tenant_revenue_trend(tenant_id=tenant_id, range_key=range)
    return SingleResponse(data=[x.model_dump() for x in data])


@router.get("/reports/transactions", response_model=PaginatedResponse)
def transactions_report(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ReportsService(db)
    items, total = svc.list_transactions(
        tenant_id=tenant_id,
        status=status,
        search=search,
        from_dt=from_date,
        to_dt=to_date,
        page=page,
        limit=limit,
    )
    skip = (page - 1) * limit
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(total=total, skip=skip, limit=limit, has_more=(skip + limit < total)),
    )


@router.get("/reports/export")
def export_transactions(
    format: str = Query(default="csv"),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ReportsService(db)
    items, _ = svc.list_transactions(
        tenant_id=tenant_id,
        status=status,
        search=search,
        from_dt=from_date,
        to_dt=to_date,
        page=page,
        limit=limit,
    )

    fmt = format.lower()
    if fmt == "pdf":
        content = svc.export_transactions_pdf(items)
        media_type = "application/pdf"
        filename = "transactions_report.pdf"
    else:
        content = svc.export_transactions_csv(items)
        media_type = "text/csv"
        filename = "transactions_report.csv"

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=content, media_type=media_type, headers=headers)
