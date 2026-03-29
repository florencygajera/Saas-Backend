"""Projects endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=PaginatedResponse)
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ProjectService(db)
    items, total = svc.list(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[item.model_dump() for item in items],
        meta=PaginationMeta(total=total, skip=skip, limit=limit, has_more=(skip + limit < total)),
    )


@router.post("", response_model=SingleResponse)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ProjectService(db)
    item = svc.create(tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=item.model_dump(), message="Project created")


@router.patch("/{project_id}", response_model=SingleResponse)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ProjectService(db)
    item = svc.update(tenant_id=tenant_id, project_id=project_id, payload=payload)
    return SingleResponse(data=item.model_dump(), message="Project updated")


@router.delete("/{project_id}", response_model=SingleResponse)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    tenant_id = require_tenant_scope(user)
    svc = ProjectService(db)
    svc.delete(tenant_id=tenant_id, project_id=project_id)
    return SingleResponse(message="Project deleted")
