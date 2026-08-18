"""The role matrix, enforced and complete.

Two properties. Drift: every registered route is either in the matrix
or explicitly public, so a new route cannot ship unguarded. Enforcement:
for every matrix row and every role, the live endpoint answers allow or
403 exactly as the matrix says, using real sessions, so a route that
forgot its dependency fails here.
"""

import json
import secrets

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from rolecall.main import app
from rolecall.roles import PUBLIC_ROUTES, ROUTE_ROLES, Role
from tests.conftest import ROLE_USERS, auth_header, login, make_user

SAMPLE_REPORT = (
    b"user,arn,user_creation_time,password_enabled,password_last_used,"
    b"password_last_changed,password_next_rotation,mfa_active,"
    b"access_key_1_active,access_key_1_last_rotated,access_key_1_last_used_date,"
    b"access_key_1_last_used_region,access_key_1_last_used_service,"
    b"access_key_2_active,access_key_2_last_rotated,access_key_2_last_used_date,"
    b"access_key_2_last_used_region,access_key_2_last_used_service,"
    b"cert_1_active,cert_1_last_rotated,cert_2_active,cert_2_last_rotated\n"
    b"matrix.user,arn:aws:iam::123456789012:user/matrix.user,"
    b"2025-01-01T00:00:00+00:00,TRUE,N/A,2025-01-01T00:00:00+00:00,N/A,TRUE,"
    b"FALSE,N/A,N/A,N/A,N/A,FALSE,N/A,N/A,N/A,N/A,FALSE,N/A,FALSE,N/A\n"
)

# How to call each governed route with a valid request, so a denial is
# provably authorization and not validation. Values are request kwargs.
CALL_PLANS: dict[str, tuple[str, str, dict[str, object]]] = {
    "GET /auth/me": ("get", "/auth/me", {}),
    "POST /auth/logout": ("post", "/auth/logout", {}),
    "GET /admin/users": ("get", "/admin/users", {}),
    "POST /admin/users": (
        "post",
        "/admin/users",
        {
            "json": {
                "username": "matrix.made",
                "password": "pw-" + secrets.token_urlsafe(16),
                "role": "reviewer",
            }
        },
    ),
    "POST /imports/credential-report": (
        "post",
        "/imports/credential-report",
        {
            "files": {"file": ("report.csv", SAMPLE_REPORT, "text/csv")},
            "data": {"captured_at": "2026-08-01T00:00:00+00:00"},
        },
    ),
    "POST /imports/authorization-details": (
        "post",
        "/imports/authorization-details",
        {
            "files": {
                "file": (
                    "details.json",
                    json.dumps({"UserDetailList": [{
                        "UserName": "matrix.auth",
                        "UserId": "AIDAMATRIX000000000001",
                        "Arn": "arn:aws:iam::123456789012:user/matrix.auth",
                        "CreateDate": "2025-01-01T00:00:00Z",
                    }]}).encode(),
                    "application/json",
                )
            },
            "data": {"captured_at": "2026-08-01T00:00:00+00:00"},
        },
    ),
    "GET /imports": ("get", "/imports", {}),
    "GET /identities": ("get", "/identities", {}),
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

    for key, (method, path, kwargs) in CALL_PLANS.items():
        allowed = ROUTE_ROLES[key]
        for role in Role:
            # Logout revokes the session it uses; give that row its own
            # disposable session so later rows keep valid tokens. The
            # import row gets a distinct capture time per call so the
            # allow case is never a duplicate rejection.
            token = (
                login(client, ROLE_USERS[role])
                if key == "POST /auth/logout"
                else tokens[role]
            )
            call_kwargs = dict(kwargs)
            if key.startswith("POST /imports/"):
                call_kwargs["data"] = {
                    "captured_at": f"2026-08-0{1 + list(Role).index(role)}T00:00:00+00:00"
                }
            response = client.request(
                method.upper(), path, headers=auth_header(token), **call_kwargs  # type: ignore[arg-type]
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
    for key, (method, path, kwargs) in CALL_PLANS.items():
        response = client.request(method.upper(), path, **kwargs)  # type: ignore[arg-type]
        assert response.status_code == 401, f"{key}: {response.status_code}"
