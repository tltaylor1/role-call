"""Application entry point.

Subphase 1.1: the skeleton. Configuration fails fast at startup,
logging is structured and allowlisted, and the two health routes are
the only surface. Everything else arrives in its own subphase.
"""

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from rolecall.config import get_settings
from rolecall.db import database_reachable
from rolecall.logs import configure_logging, log_event


def create_app() -> FastAPI:
    settings = get_settings()  # missing required keys raise here, at boot
    configure_logging(settings.log_level)

    app = FastAPI(title="role-call", version="0.1.0")

    @app.middleware("http")
    async def access_log(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        started = time.monotonic()
        response = await call_next(request)
        log_event(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round((time.monotonic() - started) * 1000, 1),
        )
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        """Liveness: the process is up and serving."""
        return {"status": "ok"}

    @app.get("/health/database")
    def health_database(response: Response) -> dict[str, str]:
        """Readiness: the database answers a round trip.

        The body never carries failure detail, only availability.
        """
        if database_reachable():
            return {"status": "ok"}
        response.status_code = 503
        return {"status": "unavailable"}

    return app


app = create_app()
