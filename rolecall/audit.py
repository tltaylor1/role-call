"""The audit spine.

record() adds a row to the caller's open transaction and never commits:
the action and its audit line share one transaction, so neither can
exist without the other. A caller that forgets to commit loses both,
which is the correct failure.

Never pass secret material in any field. The attempted username on a
failed login is stored capped at the column length; the audit table is
readable only through administrator surfaces.
"""

from sqlalchemy.orm import Session

from rolecall.models import AuditEvent


def record(
    db: Session,
    *,
    actor_username: str,
    action: str,
    actor_user_id: int | None = None,
    target: str | None = None,
    detail: str | None = None,
    ip: str | None = None,
) -> None:
    db.add(
        AuditEvent(
            actor_user_id=actor_user_id,
            actor_username=actor_username[:64],
            action=action,
            target=target[:255] if target else None,
            detail=detail[:1000] if detail else None,
            ip=ip[:64] if ip else None,
        )
    )
