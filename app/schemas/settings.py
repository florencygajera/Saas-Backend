"""Settings schemas."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ProfileOut(BaseModel):
    name: str
    email: EmailStr
    role: str
    is_verified: bool
    two_fa_enabled: bool


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PreferencesOut(BaseModel):
    timezone: str
    locale: str
    email_notifications: bool
    sms_notifications: bool


class PreferencesUpdateRequest(BaseModel):
    timezone: Optional[str] = None
    locale: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

