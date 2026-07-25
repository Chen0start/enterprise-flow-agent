from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User


def build_user_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Alice2026",
        "role": "employee",
    }

    payload.update(overrides)

    return payload


def test_create_user(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            username=" Alice ",
            email="ALICE@EXAMPLE.COM",
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
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


def test_get_user_by_id(client: TestClient) -> None:
    created_response = client.post(
        "/api/v1/users",
        json=build_user_payload(),
    )

    user_id = created_response.json()["id"]

    response = client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "alice"


def test_list_users(client: TestClient) -> None:
    client.post(
        "/api/v1/users",
        json=build_user_payload(),
    )

    client.post(
        "/api/v1/users",
        json=build_user_payload(
            username="bob",
            email="bob@example.com",
        ),
    )

    response = client.get(
        "/api/v1/users",
        params={
            "skip": 0,
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["skip"] == 0
    assert data["limit"] == 20
    assert len(data["items"]) == 2

    usernames = [item["username"] for item in data["items"]]

    assert usernames == ["alice", "bob"]


def test_duplicate_email_returns_conflict(
    client: TestClient,
) -> None:
    first_response = client.post(
        "/api/v1/users",
        json=build_user_payload(),
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            username="bob",
            email="ALICE@EXAMPLE.COM",
        ),
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == ("A user with this email already exists")


def test_duplicate_username_returns_conflict(
    client: TestClient,
) -> None:
    first_response = client.post(
        "/api/v1/users",
        json=build_user_payload(),
    )

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            username="ALICE",
            email="different@example.com",
        ),
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == ("A user with this username already exists")


def test_missing_user_returns_not_found(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == ("User 999999 was not found")


def test_invalid_email_returns_validation_error(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            email="not-an-email",
        ),
    )

    assert response.status_code == 422


def test_weak_password_returns_validation_error(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/users",
        json=build_user_payload(
            password="abcdefgh",
        ),
    )

    assert response.status_code == 422
