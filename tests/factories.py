from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
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
