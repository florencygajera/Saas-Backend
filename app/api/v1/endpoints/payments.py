"""
Payment endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, CurrentUser, require_tenant_scope
from app.core.exceptions import ForbiddenError
from app.db.session import get_db
from app.schemas.common import SingleResponse
from app.schemas.payment import PaymentStartRequest, PaymentVerifyRequest
from app.services.customer_service import CustomerService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/start", response_model=SingleResponse)
def start_payment(
    payload: PaymentStartRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role not in ("TENANT_ADMIN", "CUSTOMER"):
        raise ForbiddenError("Only tenant users can perform payment operations")
    tenant_id = require_tenant_scope(user)
    customer_id = None
    if user.role == "CUSTOMER":
        customer_id = CustomerService(db).resolve_customer_id_for_user(
            user_id=user.user_id, tenant_id=tenant_id
        )
    svc = PaymentService(db)
    result = svc.start_payment(
        appointment_id=payload.appointment_id,
        tenant_id=tenant_id,
        customer_id=customer_id,
    )
    return SingleResponse(data=result.model_dump(), message="Payment initiated")


@router.post("/verify", response_model=SingleResponse)
def verify_payment(
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role not in ("TENANT_ADMIN", "CUSTOMER"):
        raise ForbiddenError("Only tenant users can perform payment operations")
    tenant_id = require_tenant_scope(user)
    customer_id = None
    if user.role == "CUSTOMER":
        customer_id = CustomerService(db).resolve_customer_id_for_user(
            user_id=user.user_id, tenant_id=tenant_id
        )
    svc = PaymentService(db)
    result = svc.verify_payment(
        payment_id=payload.payment_id,
        otp=payload.otp,
        tenant_id=tenant_id,
        customer_id=customer_id,
    )
    return SingleResponse(data=result.model_dump(), message="Payment verified")
