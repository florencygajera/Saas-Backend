"""User settings service."""

from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError, BadRequestError
from app.core.security import verify_password, hash_password
from app.repositories.preference_repo import PreferenceRepository
from app.repositories.user_repo import UserRepository
from app.models.preference import Preference
from app.schemas.settings import (
    ProfileOut,
    ProfileUpdateRequest,
    PreferencesOut,
    PreferencesUpdateRequest,
)


class SettingsService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.pref_repo = PreferenceRepository(db)

    def get_profile(self, user_id: UUID) -> ProfileOut:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return ProfileOut(
            name=user.name,
            email=user.email,
            role=user.role,
            is_verified=user.is_verified,
            two_fa_enabled=user.two_fa_enabled,
        )

    def update_profile(self, user_id: UUID, payload: ProfileUpdateRequest) -> ProfileOut:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if payload.email and payload.email != user.email:
            existing = self.user_repo.get_by_email(payload.email)
            if existing:
                raise ConflictError("Email already in use")
            user.email = payload.email
        if payload.name:
            user.name = payload.name
        self.db.commit()
        return self.get_profile(user_id)

    def get_preferences(self, user_id: UUID, tenant_id: UUID | None) -> PreferencesOut:
        pref = self.pref_repo.get_by_user_id(user_id)
        if not pref:
            pref = Preference(user_id=user_id, tenant_id=tenant_id)
            self.db.add(pref)
            self.db.commit()
            self.db.refresh(pref)
        return PreferencesOut(
            timezone=pref.timezone,
            locale=pref.locale,
            email_notifications=pref.email_notifications,
            sms_notifications=pref.sms_notifications,
        )

    def update_preferences(
        self,
        user_id: UUID,
        tenant_id: UUID | None,
        payload: PreferencesUpdateRequest,
    ) -> PreferencesOut:
        pref = self.pref_repo.get_by_user_id(user_id)
        if not pref:
            pref = Preference(user_id=user_id, tenant_id=tenant_id)
            self.db.add(pref)
            self.db.flush()
        if payload.timezone is not None:
            pref.timezone = payload.timezone
        if payload.locale is not None:
            pref.locale = payload.locale
        if payload.email_notifications is not None:
            pref.email_notifications = payload.email_notifications
        if payload.sms_notifications is not None:
            pref.sms_notifications = payload.sms_notifications
        self.db.commit()
        return self.get_preferences(user_id, tenant_id)

    def change_password(self, user_id: UUID, old_password: str, new_password: str) -> None:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if not verify_password(old_password, user.password_hash):
            raise BadRequestError("Old password is incorrect")
        user.password_hash = hash_password(new_password)
        self.db.commit()

    def set_2fa(self, user_id: UUID, enabled: bool) -> None:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.two_fa_enabled = enabled
        self.db.commit()

