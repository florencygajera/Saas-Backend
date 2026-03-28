"""API v1 router - aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, saas, tenant, bookings, payments

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(saas.router)
api_router.include_router(tenant.router)
api_router.include_router(bookings.router)
api_router.include_router(payments.router)
