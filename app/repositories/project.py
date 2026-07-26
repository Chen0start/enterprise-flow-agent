from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectMember


class ProjectRepository:
    """Database access operations for projects."""

    @staticmethod
    def get_by_id(
        db: Session,
        project_id: int,
    ) -> Project | None:
        """Find one project by primary key."""

        return db.get(
            Project,
            project_id,
        )

    @staticmethod
    def add_project(
        db: Session,
        project: Project,
    ) -> Project:
        """Add a project to the current transaction."""

        db.add(project)
        db.flush()

        return project

    @staticmethod
    def get_membership(
        db: Session,
        *,
        project_id: int,
        user_id: int,
    ) -> ProjectMember | None:
        """Find one user's membership in a project."""

        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )

        return db.scalar(statement)

    @staticmethod
    def add_member(
        db: Session,
        membership: ProjectMember,
    ) -> ProjectMember:
        """Add a project membership to a transaction."""

        db.add(membership)
        db.flush()

        return membership

    @staticmethod
    def list_projects(
        db: Session,
        *,
        user_id: int,
        is_admin: bool,
        skip: int,
        limit: int,
    ) -> list[Project]:
        """List projects visible to one user."""

        if is_admin:
            statement = select(Project).order_by(Project.id).offset(skip).limit(limit)

        else:
            statement = (
                select(Project)
                .join(
                    ProjectMember,
                    ProjectMember.project_id == Project.id,
                )
                .where(ProjectMember.user_id == user_id)
                .order_by(Project.id)
                .offset(skip)
                .limit(limit)
            )

        return list(db.scalars(statement).all())

    @staticmethod
    def count_projects(
        db: Session,
        *,
        user_id: int,
        is_admin: bool,
    ) -> int:
        """Count projects visible to one user."""

        if is_admin:
            statement = select(func.count(Project.id))

        else:
            statement = (
                select(func.count(Project.id))
                .join(
                    ProjectMember,
                    ProjectMember.project_id == Project.id,
                )
                .where(ProjectMember.user_id == user_id)
            )

        return db.scalar(statement) or 0

    @staticmethod
    def list_members(
        db: Session,
        *,
        project_id: int,
    ) -> list[ProjectMember]:
        """List all members of a project."""

        statement = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.id)
        )

        return list(db.scalars(statement).all())
