from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectMember
from tests.factories import (
    add_test_project_member,
    create_test_project,
    create_test_user,
    get_auth_headers,
)


def create_manager_headers(
    client: TestClient,
    db_session: Session,
) -> tuple[object, dict[str, str]]:
    manager = create_test_user(
        db_session,
        username="manager",
        email="manager@example.com",
        password="Manager2026",
        role="project_manager",
    )

    headers = get_auth_headers(
        client,
        login="manager",
        password="Manager2026",
    )

    return manager, headers


def test_project_manager_can_create_project(
    client: TestClient,
    db_session: Session,
) -> None:
    manager, headers = create_manager_headers(
        client,
        db_session,
    )

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": " AI Platform ",
            "description": "Enterprise AI platform",
            "status": "active",
            "start_date": "2026-08-01",
            "planned_end_date": "2026-12-31",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "AI Platform"
    assert data["status"] == "active"
    assert data["owner_id"] == manager.id
    assert data["created_by_id"] == manager.id

    project_id = data["id"]

    stored_project = db_session.get(
        Project,
        project_id,
    )

    assert stored_project is not None

    membership = db_session.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == manager.id,
        )
    )

    assert membership is not None
    assert membership.project_role == "owner"


def test_project_creation_requires_authentication(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Alpha Project",
        },
    )

    assert response.status_code == 401


def test_employee_cannot_create_project(
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
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "Alpha Project",
        },
    )

    assert response.status_code == 403


def test_invalid_project_date_range(
    client: TestClient,
    db_session: Session,
) -> None:
    _, headers = create_manager_headers(
        client,
        db_session,
    )

    response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "name": "Invalid Dates",
            "start_date": "2026-12-31",
            "planned_end_date": "2026-08-01",
        },
    )

    assert response.status_code == 422


def test_member_only_sees_joined_projects(
    client: TestClient,
    db_session: Session,
) -> None:
    owner_one = create_test_user(
        db_session,
        username="owner1",
        email="owner1@example.com",
        password="Owner12026",
        role="project_manager",
    )

    owner_two = create_test_user(
        db_session,
        username="owner2",
        email="owner2@example.com",
        password="Owner22026",
        role="project_manager",
    )

    employee = create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    visible_project = create_test_project(
        db_session,
        owner=owner_one,
        name="Visible Project",
    )

    create_test_project(
        db_session,
        owner=owner_two,
        name="Hidden Project",
    )

    add_test_project_member(
        db_session,
        project=visible_project,
        user=employee,
    )

    headers = get_auth_headers(
        client,
        login="employee",
        password="Employee2026",
    )

    response = client.get(
        "/api/v1/projects",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == ("Visible Project")


def test_non_member_cannot_get_project(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    outsider = create_test_user(
        db_session,
        username="outsider",
        email="outsider@example.com",
        password="Outsider2026",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    headers = get_auth_headers(
        client,
        login="outsider",
        password="Outsider2026",
    )

    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_can_access_any_project(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    admin = create_test_user(
        db_session,
        username="admin",
        email="admin@example.com",
        password="Admin2026",
        role="admin",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    headers = get_auth_headers(
        client,
        login="admin",
        password="Admin2026",
    )

    response = client.get(
        f"/api/v1/projects/{project.id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == project.id


def test_owner_can_add_project_member(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    employee = create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    headers = get_auth_headers(
        client,
        login="owner",
        password="Owner2026",
    )

    response = client.post(
        f"/api/v1/projects/{project.id}/members",
        headers=headers,
        json={
            "user_id": employee.id,
            "project_role": "member",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == project.id
    assert data["user_id"] == employee.id
    assert data["project_role"] == "member"


def test_regular_member_cannot_add_members(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    member = create_test_user(
        db_session,
        username="member",
        email="member@example.com",
        password="Member2026",
    )

    target = create_test_user(
        db_session,
        username="target",
        email="target@example.com",
        password="Target2026",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    add_test_project_member(
        db_session,
        project=project,
        user=member,
        project_role="member",
    )

    headers = get_auth_headers(
        client,
        login="member",
        password="Member2026",
    )

    response = client.post(
        f"/api/v1/projects/{project.id}/members",
        headers=headers,
        json={
            "user_id": target.id,
            "project_role": "member",
        },
    )

    assert response.status_code == 403


def test_project_manager_member_can_add_members(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    manager = create_test_user(
        db_session,
        username="member-manager",
        email="member-manager@example.com",
        password="Manager2026",
    )

    target = create_test_user(
        db_session,
        username="target",
        email="target@example.com",
        password="Target2026",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    add_test_project_member(
        db_session,
        project=project,
        user=manager,
        project_role="manager",
    )

    headers = get_auth_headers(
        client,
        login="member-manager",
        password="Manager2026",
    )

    response = client.post(
        f"/api/v1/projects/{project.id}/members",
        headers=headers,
        json={
            "user_id": target.id,
            "project_role": "member",
        },
    )

    assert response.status_code == 201


def test_duplicate_project_member_returns_conflict(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    employee = create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    add_test_project_member(
        db_session,
        project=project,
        user=employee,
    )

    headers = get_auth_headers(
        client,
        login="owner",
        password="Owner2026",
    )

    response = client.post(
        f"/api/v1/projects/{project.id}/members",
        headers=headers,
        json={
            "user_id": employee.id,
            "project_role": "member",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == ("User is already a project member")


def test_inactive_user_cannot_be_added(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    inactive_user = create_test_user(
        db_session,
        username="inactive",
        email="inactive@example.com",
        password="Inactive2026",
        is_active=False,
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    headers = get_auth_headers(
        client,
        login="owner",
        password="Owner2026",
    )

    response = client.post(
        f"/api/v1/projects/{project.id}/members",
        headers=headers,
        json={
            "user_id": inactive_user.id,
            "project_role": "member",
        },
    )

    assert response.status_code == 409


def test_project_member_can_list_members(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = create_test_user(
        db_session,
        username="owner",
        email="owner@example.com",
        password="Owner2026",
        role="project_manager",
    )

    employee = create_test_user(
        db_session,
        username="employee",
        email="employee@example.com",
        password="Employee2026",
    )

    project = create_test_project(
        db_session,
        owner=owner,
    )

    add_test_project_member(
        db_session,
        project=project,
        user=employee,
    )

    headers = get_auth_headers(
        client,
        login="employee",
        password="Employee2026",
    )

    response = client.get(
        f"/api/v1/projects/{project.id}/members",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert {item["user_id"] for item in data["items"]} == {
        owner.id,
        employee.id,
    }
