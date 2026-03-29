"""Auth service - login, signup and OTP flows."""

import hashlib
import random
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import (
    UnauthorizedError,
    NotFoundError,
    ConflictError,
    BadRequestError,
)
from app.core.security import verify_password, create_access_token, hash_password
from app.models.customer import Customer
from app.models.otp_token import OtpToken
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.otp_token_repo import OtpTokenRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    UserInfo,
    SignupRequest,
    SignupResponse,
)

OTP_EXPIRY_MINUTES = 10


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_repo = OtpTokenRepository(db)

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = self.user_repo.get_by_email(payload.email)
        if not user:
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        self.user_repo.update_last_login(user)

        token = create_access_token(
            user_id=user.id,
            role=user.role,
            tenant_id=user.tenant_id,
        )

        return LoginResponse(
            access_token=token,
            user=UserInfo.model_validate(user),
        )

    def get_me(self, user_id: UUID) -> UserInfo:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserInfo.model_validate(user)

    def signup(self, payload: SignupRequest) -> SignupResponse:
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ConflictError("Email already registered")

        role = "CUSTOMER"
        tenant_id = payload.tenant_id
        if payload.create_tenant_name:
            tenant = Tenant(name=payload.create_tenant_name, plan="basic")
            self.db.add(tenant)
            self.db.flush()
            tenant_id = tenant.id
            role = "TENANT_ADMIN"
        elif tenant_id is None:
            raise BadRequestError(
                "tenant_id is required unless create_tenant_name is provided"
            )

        if tenant_id:
            tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active).first()
            if not tenant:
                raise NotFoundError("Tenant not found")

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            tenant_id=tenant_id,
            role=role,
            is_verified=False,
        )
        self.db.add(user)
        self.db.flush()

        if role == "CUSTOMER" and tenant_id:
            customer = Customer(
                tenant_id=tenant_id,
                user_id=user.id,
                name=payload.name,
                email=payload.email,
            )
            self.db.add(customer)

        otp = self._generate_otp()
        self._store_token(user, otp, purpose="EMAIL_VERIFY")
        self.db.commit()
        self.db.refresh(user)

        token = create_access_token(
            user_id=user.id,
            role=user.role,
            tenant_id=user.tenant_id,
        )

        return SignupResponse(
            access_token=token,
            user=UserInfo.model_validate(user),
            otp_sent=True,
        )

    def forgot_password(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            return
        reset_token = secrets.token_urlsafe(24)
        self._store_token(user, reset_token, purpose="PASSWORD_RESET")
        self.db.commit()

    def verify_signup_otp(self, email: str, otp: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise BadRequestError("Invalid OTP")
        otp_hash = self._hash_token(otp)
        token = self.otp_repo.get_valid_token(
            user_id=user.id, purpose="EMAIL_VERIFY", token_hash=otp_hash
        )
        if not token:
            raise BadRequestError("Invalid or expired OTP")
        token.used_at = datetime.now(timezone.utc)
        user.is_verified = True
        self.db.commit()

    def resend_signup_otp(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            return
        if user.is_verified:
            return
        otp = self._generate_otp()
        self._store_token(user, otp, purpose="EMAIL_VERIFY")
        self.db.commit()

    def _store_token(self, user: User, raw_token: str, purpose: str) -> OtpToken:
        self.otp_repo.mark_previous_tokens_used(user.id, purpose)
        token = OtpToken(
            user_id=user.id,
            tenant_id=user.tenant_id,
            purpose=purpose,
            token_hash=self._hash_token(raw_token),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
        )
        self.db.add(token)
        return token

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _generate_otp() -> str:
        return f"{random.randint(0, 999999):06d}"
