"""Team management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.team import TeamInviteRequest, TeamMemberUpdateRequest
from app.services.team_service import TeamService

router = APIRouter(prefix="/team", tags=["Team"])


@router.get("/members", response_model=PaginatedResponse)
def list_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = TeamService(db)
    items, total = svc.list_members(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(total=total, skip=skip, limit=limit, has_more=(skip + limit < total)),
    )


@router.post("/invite", response_model=SingleResponse)
def invite_member(
    payload: TeamInviteRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = TeamService(db)
    item = svc.invite_member(tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=item.model_dump(), message="Invitation created")


@router.patch("/members/{member_id}", response_model=SingleResponse)
def update_member(
    member_id: UUID,
    payload: TeamMemberUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = TeamService(db)
    item = svc.update_member(tenant_id=tenant_id, member_id=member_id, payload=payload)
    return SingleResponse(data=item.model_dump(), message="Member updated")


@router.delete("/members/{member_id}", response_model=SingleResponse)
def delete_member(
    member_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = TeamService(db)
    svc.delete_member(tenant_id=tenant_id, member_id=member_id)
    return SingleResponse(message="Member removed")
