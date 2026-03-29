"""Auth endpoints."""

from fastapi import APIRouter, Depends, BackgroundTasks
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
    RefreshTokenRequest,
    TokenRefreshResponse,
)
from app.schemas.common import SingleResponse
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload)


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_tokens(payload.refresh_token)


@router.post("/logout", response_model=SingleResponse)
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.revoke_refresh_token(payload.refresh_token)
    return SingleResponse(message="Logged out")


@router.post("/signup", response_model=SignupResponse)
def signup(
    payload: SignupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    response, otp = service.signup(payload)
    background_tasks.add_task(
        EmailService().send_otp_email,
        payload.email,
        otp,
        "EMAIL_VERIFY",
    )
    return response


@router.post("/forgot-password", response_model=SingleResponse)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    otp = service.forgot_password(payload.email)
    if otp:
        background_tasks.add_task(
            EmailService().send_otp_email,
            payload.email,
            otp,
            "PASSWORD_RESET",
        )
    return SingleResponse(message="If the account exists, reset instructions were sent.")


@router.post("/verify-otp", response_model=SingleResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.verify_signup_otp(payload.email, payload.otp)
    return SingleResponse(message="OTP verified")


@router.post("/resend-otp", response_model=SingleResponse)
def resend_otp(
    payload: ResendOtpRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    otp = service.resend_signup_otp(payload.email)
    if otp:
        background_tasks.add_task(
            EmailService().send_otp_email,
            payload.email,
            otp,
            "EMAIL_VERIFY",
        )
    return SingleResponse(message="If the account exists, a new OTP was sent.")


@router.get("/me", response_model=SingleResponse)
def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    me = service.get_me(current_user.user_id)
    return SingleResponse(data=me.model_dump())
