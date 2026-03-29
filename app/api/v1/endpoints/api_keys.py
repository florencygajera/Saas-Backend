"""API keys endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.api_key import ApiKeyCreateRequest
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.get("", response_model=PaginatedResponse)
def list_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ApiKeyService(db)
    items, total = svc.list_keys(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(total=total, skip=skip, limit=limit, has_more=(skip + limit < total)),
    )


@router.post("", response_model=SingleResponse)
def create_api_key(
    payload: ApiKeyCreateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ApiKeyService(db)
    item = svc.create_key(tenant_id=tenant_id, user_id=user.user_id, name=payload.name)
    return SingleResponse(data=item.model_dump(), message="API key generated")


@router.delete("/{key_id}", response_model=SingleResponse)
def delete_api_key(
    key_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ApiKeyService(db)
    svc.delete_key(tenant_id=tenant_id, key_id=key_id)
    return SingleResponse(message="API key deleted")
