from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.project import Project, ProjectMember
from app.models.user import User


def create_test_user(
    db: Session,
    *,
    username: str,
    email: str,
    password: str,
    role: str = "employee",
    is_active: bool = True,
) -> User:
    """Insert one user for an integration test."""

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )

    db.add(user)
    db.flush()

    return user


def get_auth_headers(
    client: TestClient,
    *,
    login: str,
    password: str,
) -> dict[str, str]:
    """Log in and return an Authorization header."""

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": login,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def create_test_project(
    db: Session,
    *,
    owner: User,
    name: str = "Alpha Project",
    status: str = "active",
) -> Project:
    """Insert a project with its owner membership."""

    project = Project(
        name=name,
        description="Integration test project",
        status=status,
        owner_id=owner.id,
        created_by_id=owner.id,
    )

    db.add(project)
    db.flush()

    membership = ProjectMember(
        project_id=project.id,
        user_id=owner.id,
        project_role="owner",
    )

    db.add(membership)
    db.flush()

    return project


def add_test_project_member(
    db: Session,
    *,
    project: Project,
    user: User,
    project_role: str = "member",
) -> ProjectMember:
    """Insert a membership for an integration test."""

    membership = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        project_role=project_role,
    )

    db.add(membership)
    db.flush()

    return membership
