"""Projects service."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut


class ProjectService:
    def __init__(self, db):
        self.repo = ProjectRepository(db)

    def list(self, tenant_id: UUID, skip: int = 0, limit: int = 50) -> tuple[list[ProjectOut], int]:
        items = self.repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.repo.count(tenant_id=tenant_id)
        return [ProjectOut.model_validate(x) for x in items], total

    def create(self, tenant_id: UUID, payload: ProjectCreate) -> ProjectOut:
        obj = Project(
            tenant_id=tenant_id,
            name=payload.name,
            progress=payload.progress,
            members_count=payload.members_count,
        )
        obj = self.repo.create(obj)
        return ProjectOut.model_validate(obj)

    def update(self, tenant_id: UUID, project_id: UUID, payload: ProjectUpdate) -> ProjectOut:
        obj = self.repo.get_by_id(project_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Project not found")
        if payload.name is not None:
            obj.name = payload.name
        if payload.progress is not None:
            obj.progress = payload.progress
        if payload.members_count is not None:
            obj.members_count = payload.members_count
        obj = self.repo.update(obj)
        return ProjectOut.model_validate(obj)

    def delete(self, tenant_id: UUID, project_id: UUID) -> None:
        obj = self.repo.get_by_id(project_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Project not found")
        self.repo.delete(obj)

