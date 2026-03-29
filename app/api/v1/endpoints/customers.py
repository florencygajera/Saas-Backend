"""
Customer CRUD endpoints — tenant admin only.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import require_tenant_admin, CurrentUser, require_tenant_scope
from app.db.session import get_db
from app.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("", response_model=SingleResponse)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = CustomerService(db)
    tenant_id = require_tenant_scope(user)
    result = svc.create(tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Customer created")


@router.get("", response_model=PaginatedResponse)
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = CustomerService(db)
    tenant_id = require_tenant_scope(user)
    items, total = svc.list(tenant_id=tenant_id, skip=skip, limit=limit)
    return PaginatedResponse(
        data=[c.model_dump() for c in items],
        meta=PaginationMeta(
            total=total, skip=skip, limit=limit, has_more=(skip + limit < total)
        ),
    )


@router.get("/{customer_id}", response_model=SingleResponse)
def get_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = CustomerService(db)
    tenant_id = require_tenant_scope(user)
    result = svc.get(customer_id, tenant_id=tenant_id)
    return SingleResponse(data=result.model_dump())


@router.put("/{customer_id}", response_model=SingleResponse)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = CustomerService(db)
    tenant_id = require_tenant_scope(user)
    result = svc.update(customer_id, tenant_id=tenant_id, payload=payload)
    return SingleResponse(data=result.model_dump(), message="Customer updated")


@router.delete("/{customer_id}", response_model=SingleResponse)
def delete_customer(
    customer_id: UUID,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_tenant_admin),
):
    svc = CustomerService(db)
    tenant_id = require_tenant_scope(user)
    svc.delete(customer_id, tenant_id=tenant_id)
    return SingleResponse(message="Customer deleted")
