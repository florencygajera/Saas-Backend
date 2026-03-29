"""Auth endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResendOtpRequest,
)
from app.schemas.common import SingleResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload)


@router.post("/signup", response_model=SignupResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.signup(payload)


@router.post("/forgot-password", response_model=SingleResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.forgot_password(payload.email)
    return SingleResponse(message="If the account exists, reset instructions were sent.")


@router.post("/verify-otp", response_model=SingleResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.verify_signup_otp(payload.email, payload.otp)
    return SingleResponse(message="OTP verified")


@router.post("/resend-otp", response_model=SingleResponse)
def resend_otp(payload: ResendOtpRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.resend_signup_otp(payload.email)
    return SingleResponse(message="If the account exists, a new OTP was sent.")


@router.get("/me", response_model=SingleResponse)
def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    me = service.get_me(current_user.user_id)
    return SingleResponse(data=me.model_dump())
