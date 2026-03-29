"""Auth schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserInfo(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    tenant_id: Optional[UUID] = None
    tenant_name: Optional[str] = None
    is_active: bool
    is_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

    model_config = ConfigDict(extra="forbid")


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfo


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    tenant_id: Optional[UUID] = None
    create_tenant_name: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

    model_config = ConfigDict(extra="forbid")


class ResendOtpRequest(BaseModel):
    email: EmailStr


class SignupResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfo
    otp_sent: bool = True


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
