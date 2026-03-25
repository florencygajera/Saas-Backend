"""
Payment endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse
from app.schemas.payment import PaymentStartRequest, PaymentVerifyRequest
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/start", response_model=SingleResponse)
def start_payment(
    payload: PaymentStartRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = PaymentService(db)
    assert user.tenant_id is not None, "Tenant ID is required for payment operations"
    result = svc.start_payment(
        appointment_id=payload.appointment_id,
        tenant_id=user.tenant_id,
    )
    return SingleResponse(data=result.model_dump(), message="Payment initiated")


@router.post("/verify", response_model=SingleResponse)
def verify_payment(
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = PaymentService(db)
    assert user.tenant_id is not None, "Tenant ID is required for payment operations"
    result = svc.verify_payment(
        payment_id=payload.payment_id,
        otp=payload.otp,
        tenant_id=user.tenant_id,
    )
    return SingleResponse(data=result.model_dump(), message="Payment verified")
