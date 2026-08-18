"""Application entry point.

Subphase 1.2: operators, roles, sessions, and the audit spine, on the
1.1 foundation. Error discipline lives here: validation failures and
unhandled errors answer with fixed bodies that repeat nothing the
caller sent; the detail goes to the server log, never the response.
"""

import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from rolecall.bootstrap import bootstrap_admin
from rolecall.config import get_settings
from rolecall.db import database_reachable, get_engine
from rolecall.logs import configure_logging, log_event
from rolecall.routes import admin, auth


def create_app() -> FastAPI:
    settings = get_settings()  # missing required keys raise here, at boot
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        from sqlalchemy.orm import Session

        with Session(get_engine()) as db:
            bootstrap_admin(db, settings)
        yield

    app = FastAPI(title="role-call", version="0.2.0", lifespan=lifespan)

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

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # The fixed body: what the caller sent is never repeated back.
        log_event("validation_rejected", path=request.url.path)
        return JSONResponse(status_code=422, content={"detail": "invalid request"})

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        log_event("unhandled_error", path=request.url.path, include_traceback=True)
        return JSONResponse(status_code=500, content={"detail": "internal error"})

    @app.get("/health")
    def health() -> dict[str, str]:
        """Liveness: the process is up and serving."""
        return {"status": "ok"}

    @app.get("/health/database")
    def health_database(response: Response) -> dict[str, str]:
        """Readiness: the database answers a round trip."""
        if database_reachable():
            return {"status": "ok"}
        response.status_code = 503
        return {"status": "unavailable"}

    app.include_router(auth.router)
    app.include_router(admin.router)
    return app


app = create_app()
