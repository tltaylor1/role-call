"""Configuration fails fast: a missing required key raises immediately."""

import pytest
from pydantic import ValidationError

from rolecall.config import Settings


def test_missing_database_url_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ROLECALL_DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_present_database_url_loads(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROLECALL_DATABASE_URL", "postgresql+psycopg://example")
    settings = Settings()
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_log_level_defaults_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROLECALL_DATABASE_URL", "postgresql+psycopg://example")
    monkeypatch.delenv("ROLECALL_LOG_LEVEL", raising=False)
    assert Settings().log_level == "INFO"
