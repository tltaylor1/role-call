"""Application configuration.

Every required key fails fast: a missing value stops the process at
startup with a clear error, rather than surfacing later as a confusing
failure mid-request. Optional keys carry their default here, so this
file is the complete inventory of what configures the application.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ROLECALL_")

    # Required: no default, so a missing value raises at startup.
    database_url: str

    # Optional, with the default visible here.
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Build settings once and reuse them.

    The cache means the fail-fast check runs exactly once, at first use,
    which the application arranges to be startup.
    """
    return Settings()
