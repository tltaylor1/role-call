"""The two health routes: liveness is unconditional, readiness tells the truth."""

from fastapi.testclient import TestClient

from rolecall.main import app

client = TestClient(app)


def test_liveness_is_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_unavailable_without_a_database() -> None:
    # conftest points the database URL at a closed port, so readiness
    # must answer 503 with a body that carries no failure detail.
    response = client.get("/health/database")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
