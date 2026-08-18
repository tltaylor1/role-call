"""The credential report importer: append-only, one transaction.

Everything one import creates, the account row if new, the snapshot,
any new identities, every observation, and the audit line, commits
together or not at all. Nothing is ever updated in place; a re-import
of the same capture is rejected by the snapshot's unique constraint,
and a new capture only adds rows (D-006).
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rolecall import audit
from rolecall.ingest.credential_report import ParsedReport
from rolecall.models import Account, Identity, Observation, Snapshot

SOURCE = "credential_report"


class DuplicateSnapshot(ValueError):
    """This account, source, and capture time were already imported."""


class CaptureTimeInvalid(ValueError):
    """States the rule; never echoes the value."""


@dataclass
class ImportResult:
    account: str
    captured_at: datetime
    identities_new: int
    identities_known: int
    observations: int
    skipped_rows: int


def import_credential_report(
    db: Session,
    *,
    report: ParsedReport,
    captured_at: datetime,
    source_filename: str | None,
    actor_user_id: int,
    actor_username: str,
) -> ImportResult:
    if captured_at.tzinfo is None:
        raise CaptureTimeInvalid("capture time must carry a timezone")
    captured_at = captured_at.astimezone(UTC)
    if captured_at > datetime.now(UTC) + timedelta(minutes=5):
        raise CaptureTimeInvalid("capture time is in the future")

    account = db.execute(
        select(Account).where(Account.provider_account_id == report.account_id)
    ).scalar_one_or_none()
    if account is None:
        account = Account(
            provider_account_id=report.account_id,
            display_name=report.account_id,
        )
        db.add(account)
        db.flush()

    duplicate = db.execute(
        select(Snapshot).where(
            Snapshot.account_id == account.id,
            Snapshot.source == SOURCE,
            Snapshot.captured_at == captured_at,
        )
    ).scalar_one_or_none()
    if duplicate is not None:
        db.rollback()
        raise DuplicateSnapshot(
            "this account, source, and capture time were already imported"
        )

    snapshot = Snapshot(
        account_id=account.id,
        source=SOURCE,
        captured_at=captured_at,
        source_filename=(source_filename or "")[:255] or None,
        row_count=len(report.rows),
        skipped_count=report.skipped,
    )
    db.add(snapshot)
    db.flush()

    known = {
        identity.provider_identifier: identity
        for identity in db.execute(
            select(Identity).where(Identity.account_id == account.id)
        ).scalars()
    }
    new_count = 0
    seen_this_snapshot: set[str] = set()
    skipped = report.skipped
    observations = 0
    for row in report.rows:
        # A file repeating the same principal would violate the
        # one-observation-per-identity rule; the repeat is a skip.
        if row.provisional_key in seen_this_snapshot:
            skipped += 1
            continue
        seen_this_snapshot.add(row.provisional_key)
        identity = known.get(row.provisional_key)
        if identity is None:
            identity = Identity(
                account_id=account.id,
                provider_identifier=row.provisional_key,
                provisional=True,
                identity_type="root" if row.is_root else "user",
                first_display_name=row.display_name,
            )
            db.add(identity)
            db.flush()
            known[row.provisional_key] = identity
            new_count += 1
        db.add(
            Observation(
                snapshot_id=snapshot.id,
                identity_id=identity.id,
                display_name=row.display_name,
                arn=row.arn,
                identity_created_at=row.identity_created_at,
                password_enabled=row.password_enabled,
                password_last_used=row.password_last_used,
                password_last_changed=row.password_last_changed,
                mfa_active=row.mfa_active,
                key1_active=row.key1_active,
                key1_last_rotated=row.key1_last_rotated,
                key1_last_used=row.key1_last_used,
                key1_last_service=row.key1_last_service,
                key2_active=row.key2_active,
                key2_last_rotated=row.key2_last_rotated,
                key2_last_used=row.key2_last_used,
                key2_last_service=row.key2_last_service,
                cert1_active=row.cert1_active,
                cert2_active=row.cert2_active,
            )
        )
        observations += 1

    snapshot.skipped_count = skipped
    audit.record(
        db,
        actor_user_id=actor_user_id,
        actor_username=actor_username,
        action="snapshot_imported",
        target=f"account {report.account_id}",
        detail=(
            f"source {SOURCE}, captured {captured_at.isoformat()}, "
            f"{observations} observations, {new_count} new identities, "
            f"{skipped} skipped"
        ),
    )
    try:
        db.commit()
    except IntegrityError as exc:
        # The unique constraint is the last word on duplicates.
        db.rollback()
        raise DuplicateSnapshot(
            "this account, source, and capture time were already imported"
        ) from exc

    return ImportResult(
        account=report.account_id,
        captured_at=captured_at,
        identities_new=new_count,
        identities_known=len(seen_this_snapshot) - new_count,
        observations=observations,
        skipped_rows=skipped,
    )
