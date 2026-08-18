"""User management: create, list, and the edges that matter."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from rolecall.models import AuditEvent
from rolecall.roles import Role
from tests.conftest import auth_header, login, make_user

NEW_USER_PASSWORD = "pw-" + __import__("secrets").token_urlsafe(16)


def _admin_token(client: TestClient, db: Session) -> str:
    make_user(db, Role.administrator)
    return login(client, "test.admin")


def test_create_then_list(client: TestClient, db: Session) -> None:
    token = _admin_token(client, db)
    r = client.post(
        "/admin/users",
        headers=auth_header(token),
        json={
            "username": "new.reviewer",
            "password": NEW_USER_PASSWORD,
            "role": "reviewer",
        },
    )
    assert r.status_code == 201
    names = [u["username"] for u in client.get(
        "/admin/users", headers=auth_header(token)
    ).json()]
    assert "new.reviewer" in names
    # The creation is attributed in the audit table.
    row = db.execute(
        select(AuditEvent).where(AuditEvent.action == "user_created")
    ).scalar_one()
    assert row.actor_username == "test.admin"
    assert row.target == "new.reviewer"


def test_created_user_can_sign_in(client: TestClient, db: Session) -> None:
    token = _admin_token(client, db)
    client.post(
        "/admin/users",
        headers=auth_header(token),
        json={
            "username": "new.operator",
            "password": NEW_USER_PASSWORD,
            "role": "operator",
        },
    )
    r = client.post(
        "/auth/login",
        json={"username": "new.operator", "password": NEW_USER_PASSWORD},
    )
    assert r.status_code == 200
    assert r.json()["role"] == "operator"


def test_duplicate_username_conflicts(client: TestClient, db: Session) -> None:
    token = _admin_token(client, db)
    body = {
        "username": "twice.made",
        "password": NEW_USER_PASSWORD,
        "role": "reviewer",
    }
    assert client.post(
        "/admin/users", headers=auth_header(token), json=body
    ).status_code == 201
    assert client.post(
        "/admin/users", headers=auth_header(token), json=body
    ).status_code == 409


def test_short_password_states_the_policy(client: TestClient, db: Session) -> None:
    token = _admin_token(client, db)
    r = client.post(
        "/admin/users",
        headers=auth_header(token),
        json={"username": "short.pass", "password": "short", "role": "reviewer"},
    )
    assert r.status_code == 422
    assert "at least 12 characters" in r.json()["detail"]
    assert "short" != r.json()["detail"]  # states the policy, not the input


def test_invalid_role_is_rejected_generically(client: TestClient, db: Session) -> None:
    token = _admin_token(client, db)
    r = client.post(
        "/admin/users",
        headers=auth_header(token),
        json={
            "username": "bad.role",
            "password": NEW_USER_PASSWORD,
            "role": "supreme-leader",
        },
    )
    assert r.status_code == 422
    assert "supreme-leader" not in r.text
