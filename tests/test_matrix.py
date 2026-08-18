"""The role matrix, enforced and complete.

Two properties. Drift: every registered route is either in the matrix
or explicitly public, so a new route cannot ship unguarded. Enforcement:
for every matrix row and every role, the live endpoint answers allow or
403 exactly as the matrix says, using real sessions, so a route that
forgot its dependency fails here.
"""

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from rolecall.main import app
from rolecall.roles import PUBLIC_ROUTES, ROUTE_ROLES, Role
from tests.conftest import ROLE_USERS, auth_header, login, make_user

# How to call each governed route with a valid request, so a denial is
# provably authorization and not validation.
CALL_PLANS: dict[str, tuple[str, str, dict[str, object] | None]] = {
    "GET /auth/me": ("get", "/auth/me", None),
    "POST /auth/logout": ("post", "/auth/logout", None),
    "GET /admin/users": ("get", "/admin/users", None),
    "POST /admin/users": (
        "post",
        "/admin/users",
        {
            "username": "matrix.made",
            "password": "pw-" + __import__("secrets").token_urlsafe(16),
            "role": "reviewer",
        },
    ),
}


def test_every_route_is_governed_or_named_public() -> None:
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in route.methods - {"HEAD", "OPTIONS"}:
            key = f"{method} {route.path}"
            assert key in ROUTE_ROLES or key in PUBLIC_ROUTES, (
                f"route {key} is neither in ROUTE_ROLES nor PUBLIC_ROUTES"
            )


def test_every_matrix_row_has_a_call_plan() -> None:
    assert set(CALL_PLANS) == set(ROUTE_ROLES)


def test_matrix_rows_are_enforced_for_every_role(
    client: TestClient, db: Session
) -> None:
    for role in Role:
        make_user(db, role)
    tokens = {role: login(client, ROLE_USERS[role]) for role in Role}

    for key, allowed in ROUTE_ROLES.items():
        method, path, body = CALL_PLANS[key]
        for role in Role:
            # Logout revokes the session it uses; give that row its own
            # disposable session so later rows keep valid tokens.
            token = (
                login(client, ROLE_USERS[role])
                if key == "POST /auth/logout"
                else tokens[role]
            )
            response = client.request(
                method.upper(), path, headers=auth_header(token), json=body
            )
            if role in allowed:
                assert response.status_code < 400, (
                    f"{key} should admit {role}: {response.status_code}"
                )
            else:
                assert response.status_code == 403, (
                    f"{key} should refuse {role}: {response.status_code}"
                )
                assert "requires role" in response.json()["detail"]


def test_unauthenticated_calls_get_401_not_403(client: TestClient) -> None:
    for key, (method, path, body) in CALL_PLANS.items():
        response = client.request(method.upper(), path, json=body)
        assert response.status_code == 401, f"{key}: {response.status_code}"
