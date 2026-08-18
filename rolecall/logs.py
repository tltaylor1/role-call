"""Structured logging with a field allowlist.

Log lines are JSON objects, and only fields named in the allowlist may
appear in them. The allowlist is the control that keeps secrets and raw
user input out of the logs: a field that is not on the list raises
immediately, at the call site, in every environment. Blocking is
deliberate; a warning would let the value through exactly when it
matters.

Growing the allowlist is a reviewed change to this file, which is the
point: adding a new logged field is a decision, not an accident.
"""

import json
import logging
from datetime import UTC, datetime

ALLOWED_FIELDS = frozenset(
    {
        "event",
        "method",
        "path",
        "status",
        "duration_ms",
        "actor",
        "role",
        "source",
        "count",
        "detail",
    }
)


class DisallowedLogField(ValueError):
    """A log call tried to include a field the allowlist does not name."""


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        line = {
            "time": datetime.now(UTC).isoformat(timespec="seconds"),
            "level": record.levelname,
        }
        # Structured fields arrive via the record's extra dict.
        line.update(getattr(record, "fields", {"event": record.getMessage()}))
        return json.dumps(line)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLineFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())


def log_event(event: str, **fields: object) -> None:
    """Emit one structured log line, allowlist enforced."""
    rejected = set(fields) - ALLOWED_FIELDS
    if rejected:
        raise DisallowedLogField(
            "log fields not on the allowlist: " + ", ".join(sorted(rejected))
        )
    logging.getLogger("rolecall").info(
        event, extra={"fields": {"event": event, **fields}}
    )
