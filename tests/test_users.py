from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from tests.factories import (
    create_test_user,
    get_auth_headers,
)


def build_user_payload(
    **overrides: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Alice2026",
        "role": "employee",
    }

    payload.update(overrides)

    return payload


def create_admin_headers(
    client: TestClient,
    db_session: Session,
) -> dict[str, str]:
    create_test_user(
        db_session,
        username="admin",
        email="admin@example.com",
        password="Admin2026",
        role="admin",
    )

    return get_auth_headers(
        client,
        login="admin",
        password="Admin2026",
    )


def test_admin_can_create_user(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            username=" Alice ",
            email="ALICE@EXAMPLE.COM",
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "employee"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data

    stored_user = db_session.scalar(select(User).where(User.email == "alice@example.com"))

    assert stored_user is not None
    assert stored_user.password_hash != "Alice2026"

    assert verify_password(
        "Alice2026",
        stored_user.password_hash,
    )


def test_create_user_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/users",
        json=build_user_payload(),
    )

    assert response.status_code == 401


def test_employee_cannot_create_user(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
        role="employee",
    )

    headers = get_auth_headers(
        client,
        login="employee",
        password="Employee2026",
    )

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("Administrator permission required")


def test_duplicate_email_returns_conflict(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    first_response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(),
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            username="bob",
            email="ALICE@EXAMPLE.COM",
        ),
    )

    assert duplicate_response.status_code == 409


def test_duplicate_username_returns_conflict(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    first_response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(),
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            username="ALICE",
            email="different@example.com",
        ),
    )

    assert duplicate_response.status_code == 409


def test_admin_can_list_users(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(),
    )

    client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            username="bob",
            email="bob@example.com",
        ),
    )

    response = client.get(
        "/api/v1/users",
        headers=headers,
        params={
            "skip": 0,
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert len(data["items"]) == 3

    usernames = [item["username"] for item in data["items"]]

    assert usernames == [
        "admin",
        "alice",
        "bob",
    ]


def test_employee_cannot_list_users(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    headers = get_auth_headers(
        client,
        login="employee",
        password="Employee2026",
    )

    response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert response.status_code == 403


def test_employee_can_get_self(
    client: TestClient,
    db_session: Session,
) -> None:
    employee = create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    headers = get_auth_headers(
        client,
        login="employee",
        password="Employee2026",
    )

    response = client.get(
        f"/api/v1/users/{employee.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == employee.id


def test_employee_cannot_get_another_user(
    client: TestClient,
    db_session: Session,
) -> None:
    create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    another_user = create_test_user(
        db_session,
        username="another",
        email="another@example.com",
        password="Another2026",
    )

    headers = get_auth_headers(
        client,
        login="employee",
        password="Employee2026",
    )

    response = client.get(
        f"/api/v1/users/{another_user.id}",
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_gets_missing_user_not_found(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    response = client.get(
        "/api/v1/users/999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_invalid_email_returns_validation_error(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            email="not-an-email",
        ),
    )

    assert response.status_code == 422


def test_weak_password_returns_validation_error(
    client: TestClient,
    db_session: Session,
) -> None:
    headers = create_admin_headers(
        client,
        db_session,
    )

    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=build_user_payload(
            password="abcdefgh",
        ),
    )

    assert response.status_code == 422
