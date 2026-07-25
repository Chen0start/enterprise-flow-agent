from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from tests.factories import (
    create_test_user,
    get_auth_headers,
)


def test_login_with_username(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="alice",
        email="alice@example.com",
        password="Alice2026",
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "alice",
            "password": "Alice2026",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 20


def test_login_with_email(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="alice",
        email="alice@example.com",
        password="Alice2026",
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "ALICE@EXAMPLE.COM",
            "password": "Alice2026",
        },
    )

    assert response.status_code == 200


def test_login_with_wrong_password(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="alice",
        email="alice@example.com",
        password="Alice2026",
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "alice",
            "password": "WrongPassword2026",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Incorrect username or password")


def test_inactive_user_cannot_login(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="disabled",
        email="disabled@example.com",
        password="Disabled2026",
        is_active=False,
    )

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "disabled",
            "password": "Disabled2026",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("User account is inactive")


def test_get_current_user(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="alice",
        email="alice@example.com",
        password="Alice2026",
    )

    headers = get_auth_headers(
        client,
        login="alice",
        password="Alice2026",
    )

    response = client.get(
        "/api/v1/users/me",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert response.json()["email"] == ("alice@example.com")


def test_current_user_requires_token(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_malformed_token_is_rejected(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer not-a-real-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Could not validate credentials")


def test_expired_token_is_rejected(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_test_user(
        db_session,
        username="alice",
        email="alice@example.com",
        password="Alice2026",
    )

    expired_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": (f"Bearer {expired_token}"),
        },
    )

    assert response.status_code == 401
