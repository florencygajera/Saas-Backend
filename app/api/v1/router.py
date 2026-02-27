"""
API v1 router — aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    saas,
    services,
    staff,
    customers,
    appointments,
    bookings,
    payments,
    analytics,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(saas.router)
api_router.include_router(services.router)
api_router.include_router(staff.router)
api_router.include_router(customers.router)
api_router.include_router(appointments.router)
api_router.include_router(bookings.router)
api_router.include_router(payments.router)
api_router.include_router(analytics.router)
