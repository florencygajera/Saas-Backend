"""Settings endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.common import SingleResponse
from app.schemas.settings import (
    ProfileUpdateRequest,
    PreferencesUpdateRequest,
    PasswordChangeRequest,
)
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/profile", response_model=SingleResponse)
def get_profile(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    profile = svc.get_profile(user.user_id)
    return SingleResponse(data=profile.model_dump())


@router.put("/profile", response_model=SingleResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    profile = svc.update_profile(user.user_id, payload)
    return SingleResponse(data=profile.model_dump(), message="Profile updated")


@router.get("/preferences", response_model=SingleResponse)
def get_preferences(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    pref = svc.get_preferences(user.user_id, user.tenant_id)
    return SingleResponse(data=pref.model_dump())


@router.put("/preferences", response_model=SingleResponse)
def update_preferences(
    payload: PreferencesUpdateRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    pref = svc.update_preferences(user.user_id, user.tenant_id, payload)
    return SingleResponse(data=pref.model_dump(), message="Preferences updated")


@router.put("/security/password", response_model=SingleResponse)
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    svc.change_password(user.user_id, payload.old_password, payload.new_password)
    return SingleResponse(message="Password updated")


@router.post("/security/2fa/enable", response_model=SingleResponse)
def enable_2fa(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    svc.set_2fa(user.user_id, True)
    return SingleResponse(message="2FA enabled")


@router.post("/security/2fa/disable", response_model=SingleResponse)
def disable_2fa(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    svc = SettingsService(db)
    svc.set_2fa(user.user_id, False)
    return SingleResponse(message="2FA disabled")
