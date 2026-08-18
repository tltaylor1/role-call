"""The no-echo canary: what a caller sends never comes back at them."""

from fastapi.testclient import TestClient

CANARY = "canary-string-that-must-not-reflect"


def test_validation_failure_echoes_nothing(client: TestClient) -> None:
    r = client.post(
        "/auth/login", json={"username": CANARY + "x" * 100, "password": 12345}
    )
    assert r.status_code == 422
    assert r.json() == {"detail": "invalid request"}
    assert CANARY not in r.text


def test_wrong_content_type_echoes_nothing(client: TestClient) -> None:
    r = client.post("/auth/login", content=CANARY, headers={"content-type": "text/plain"})
    assert r.status_code == 422
    assert CANARY not in r.text


def test_login_failure_echoes_nothing(client: TestClient) -> None:
    r = client.post(
        "/auth/login", json={"username": CANARY[:40], "password": CANARY}
    )
    assert r.status_code == 401
    assert CANARY not in r.text
    assert CANARY[:40] not in r.text
