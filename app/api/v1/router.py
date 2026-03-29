"""API v1 router - aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    saas,
    tenant,
    bookings,
    payments,
    tenant_insights,
    billing,
    settings,
    team,
    api_keys,
    projects,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(saas.router)
api_router.include_router(tenant.router)
api_router.include_router(bookings.router)
api_router.include_router(payments.router)
api_router.include_router(tenant_insights.router)
api_router.include_router(billing.router)
api_router.include_router(settings.router)
api_router.include_router(team.router)
api_router.include_router(api_keys.router)
api_router.include_router(projects.router)
