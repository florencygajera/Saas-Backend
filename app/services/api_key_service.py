"""API key service."""

import hashlib
import secrets
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.api_key import ApiKey
from app.repositories.api_key_repo import ApiKeyRepository
from app.schemas.api_key import ApiKeyOut, ApiKeyCreateResponse


class ApiKeyService:
    def __init__(self, db):
        self.db = db
        self.repo = ApiKeyRepository(db)

    def list_keys(self, tenant_id: UUID, skip: int = 0, limit: int = 50) -> tuple[list[ApiKeyOut], int]:
        items = self.repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.repo.count(tenant_id=tenant_id)
        return [ApiKeyOut.model_validate(x) for x in items], total

    def create_key(self, tenant_id: UUID, user_id: UUID, name: str) -> ApiKeyCreateResponse:
        raw_key = f"sk_live_{secrets.token_urlsafe(24)}"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        prefix = raw_key[:12]
        item = ApiKey(
            tenant_id=tenant_id,
            created_by_user_id=user_id,
            name=name,
            key_prefix=prefix,
            key_hash=key_hash,
            is_active=True,
        )
        item = self.repo.create(item)
        return ApiKeyCreateResponse(
            id=item.id,
            name=item.name,
            key_prefix=item.key_prefix,
            is_active=item.is_active,
            created_at=item.created_at,
            last_used_at=item.last_used_at,
            api_key=raw_key,
        )

    def delete_key(self, tenant_id: UUID, key_id: UUID) -> None:
        item = self.repo.get_by_id(key_id, tenant_id=tenant_id)
        if not item:
            raise NotFoundError("API key not found")
        self.repo.delete(item)

