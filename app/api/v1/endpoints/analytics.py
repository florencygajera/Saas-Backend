"""
Tenant analytics endpoint — tenant admin gets their own stats.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/tenant", tags=["Tenant Analytics"])


@router.get("/stats", response_model=SingleResponse)
def tenant_stats(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    analytics = AnalyticsService(db)
    stats = analytics.get_tenant_stats(user.tenant_id)
    return SingleResponse(data=stats.model_dump())
