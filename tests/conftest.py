"""Test environment.

Tests run without a live database. The URL points at a closed local
port so anything that does reach for a connection fails fast instead of
hanging, and the readiness test exercises exactly that path on purpose.
"""

import os

os.environ.setdefault(
    "ROLECALL_DATABASE_URL",
    "postgresql+psycopg://unused:unused@127.0.0.1:9/unused?connect_timeout=1",
)
