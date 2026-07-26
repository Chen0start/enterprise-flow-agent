from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    PermissionDeniedError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.user import UserRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectMemberAdd,
    ProjectRole,
)
from app.schemas.user import UserRole


class ProjectService:
    """Business logic for projects and memberships."""

    @staticmethod
    def create_project(
        db: Session,
        *,
        payload: ProjectCreate,
        current_user: User,
    ) -> Project:
        """Create a project and make its creator the owner."""

        allowed_roles = {
            UserRole.ADMIN.value,
            UserRole.PROJECT_MANAGER.value,
        }

        if current_user.role not in allowed_roles:
            raise PermissionDeniedError("Project manager or administrator permission required")

        project = Project(
            name=payload.name,
            description=payload.description,
            status=payload.status.value,
            owner_id=current_user.id,
            created_by_id=current_user.id,
            start_date=payload.start_date,
            planned_end_date=payload.planned_end_date,
        )

        try:
            ProjectRepository.add_project(
                db,
                project,
            )

            owner_membership = ProjectMember(
                project_id=project.id,
                user_id=current_user.id,
                project_role=ProjectRole.OWNER.value,
            )

            ProjectRepository.add_member(
                db,
                owner_membership,
            )

            db.commit()
            db.refresh(project)

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictError("Project could not be created") from exc

        return project

    @staticmethod
    def list_projects(
        db: Session,
        *,
        current_user: User,
        skip: int,
        limit: int,
    ) -> tuple[list[Project], int]:
        """Return projects visible to the current user."""

        is_admin = current_user.role == UserRole.ADMIN.value

        projects = ProjectRepository.list_projects(
            db,
            user_id=current_user.id,
            is_admin=is_admin,
            skip=skip,
            limit=limit,
        )

        total = ProjectRepository.count_projects(
            db,
            user_id=current_user.id,
            is_admin=is_admin,
        )

        return projects, total

    @staticmethod
    def get_project(
        db: Session,
        *,
        project_id: int,
        current_user: User,
    ) -> Project:
        """Return a project visible to the current user."""

        project = ProjectRepository.get_by_id(
            db,
            project_id,
        )

        if project is None:
            raise ResourceNotFoundError(f"Project {project_id} was not found")

        is_admin = current_user.role == UserRole.ADMIN.value

        if not is_admin:
            membership = ProjectRepository.get_membership(
                db,
                project_id=project_id,
                user_id=current_user.id,
            )

            if membership is None:
                raise PermissionDeniedError("You do not have access to this project")

        return project

    @staticmethod
    def add_member(
        db: Session,
        *,
        project_id: int,
        payload: ProjectMemberAdd,
        current_user: User,
    ) -> ProjectMember:
        """Add a user to a project."""

        ProjectService.get_project(
            db,
            project_id=project_id,
            current_user=current_user,
        )

        is_admin = current_user.role == UserRole.ADMIN.value

        if not is_admin:
            actor_membership = ProjectRepository.get_membership(
                db,
                project_id=project_id,
                user_id=current_user.id,
            )

            allowed_project_roles = {
                ProjectRole.OWNER.value,
                ProjectRole.MANAGER.value,
            }

            if (
                actor_membership is None
                or actor_membership.project_role not in allowed_project_roles
            ):
                raise PermissionDeniedError("Project owner or manager permission required")

        target_user = UserRepository.get_by_id(
            db,
            payload.user_id,
        )

        if target_user is None:
            raise ResourceNotFoundError(f"User {payload.user_id} was not found")

        if not target_user.is_active:
            raise ResourceConflictError("Inactive users cannot be added to projects")

        existing_membership = ProjectRepository.get_membership(
            db,
            project_id=project_id,
            user_id=payload.user_id,
        )

        if existing_membership is not None:
            raise ResourceConflictError("User is already a project member")

        membership = ProjectMember(
            project_id=project_id,
            user_id=payload.user_id,
            project_role=payload.project_role.value,
        )

        try:
            ProjectRepository.add_member(
                db,
                membership,
            )

            db.commit()
            db.refresh(membership)

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictError("User is already a project member") from exc

        return membership

    @staticmethod
    def list_members(
        db: Session,
        *,
        project_id: int,
        current_user: User,
    ) -> list[ProjectMember]:
        """Return members of an accessible project."""

        ProjectService.get_project(
            db,
            project_id=project_id,
            current_user=current_user,
        )

        return ProjectRepository.list_members(
            db,
            project_id=project_id,
        )
