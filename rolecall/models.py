"""The tables this subphase owns: users, sessions, audit.

Timestamps are timezone-aware and set in Python rather than by the
database server, which keeps the models portable between the production
database and the in-memory database the unit tests run on; the
migration drift check in the pipeline guards the production side.
"""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from rolecall.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(72))
    # Stored as its string value; the Role enum is the application-side
    # vocabulary and the single place the valid values live.
    role: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # The SHA-256 of the token; the token itself is never stored.
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    # The provider's account number, derived from the imported file's own
    # content, never from a filename or a form field (D-008).
    provider_account_id: Mapped[str] = mapped_column(
        String(32), unique=True, index=True
    )
    display_name: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class Snapshot(Base):
    __tablename__ = "snapshots"
    # One import of one source file for one account at one capture time;
    # the unique constraint is the duplicate-import rejection.
    __table_args__ = (
        UniqueConstraint("account_id", "source", "captured_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    source: Mapped[str] = mapped_column(String(32))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    # Client-supplied, stored for the operator's reference, trusted for
    # nothing (D-008).
    source_filename: Mapped[str | None] = mapped_column(String(255), default=None)
    row_count: Mapped[int] = mapped_column(default=0)
    skipped_count: Mapped[int] = mapped_column(default=0)


class Identity(Base):
    __tablename__ = "identities"
    __table_args__ = (
        UniqueConstraint("account_id", "provider_identifier"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    # D-016: the immutable key. When the source file carries no unique
    # identifier, this holds a provisional key derived from immutable
    # content (D-029), upgraded when a source that knows arrives.
    provider_identifier: Mapped[str] = mapped_column(String(128), index=True)
    provisional: Mapped[bool] = mapped_column(default=False)
    identity_type: Mapped[str] = mapped_column(String(16))
    first_display_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class Observation(Base):
    __tablename__ = "observations"
    # What one snapshot said about one identity, append-only, never
    # updated (D-006); state is derived from these at read time.
    __table_args__ = (
        UniqueConstraint("snapshot_id", "identity_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshots.id"))
    identity_id: Mapped[int] = mapped_column(ForeignKey("identities.id"))
    display_name: Mapped[str] = mapped_column(String(255))
    arn: Mapped[str | None] = mapped_column(String(2048), default=None)
    identity_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    password_enabled: Mapped[bool | None] = mapped_column(default=None)
    password_last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    password_last_changed: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    mfa_active: Mapped[bool | None] = mapped_column(default=None)
    key1_active: Mapped[bool | None] = mapped_column(default=None)
    key1_last_rotated: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    key1_last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    key1_last_service: Mapped[str | None] = mapped_column(String(64), default=None)
    key2_active: Mapped[bool | None] = mapped_column(default=None)
    key2_last_rotated: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    key2_last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    key2_last_service: Mapped[str | None] = mapped_column(String(64), default=None)
    cert1_active: Mapped[bool | None] = mapped_column(default=None)
    cert2_active: Mapped[bool | None] = mapped_column(default=None)
    # Authorization-details fields; null for credential-report rows.
    role_last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )
    role_last_used_region: Mapped[str | None] = mapped_column(
        String(64), default=None
    )
    trust_policy: Mapped[dict[str, object] | None] = mapped_column(JSON, default=None)
    tags: Mapped[dict[str, str] | None] = mapped_column(JSON, default=None)
    attached_policies: Mapped[list[dict[str, str]] | None] = mapped_column(
        JSON, default=None
    )
    inline_policy_names: Mapped[list[str] | None] = mapped_column(JSON, default=None)
    group_names: Mapped[list[str] | None] = mapped_column(JSON, default=None)


class Group(Base):
    """Groups are governable privilege sources, never actors (D-019)."""

    __tablename__ = "groups"
    __table_args__ = (UniqueConstraint("account_id", "provider_identifier"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    provider_identifier: Mapped[str] = mapped_column(String(128), index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class GroupObservation(Base):
    __tablename__ = "group_observations"
    __table_args__ = (UniqueConstraint("snapshot_id", "group_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshots.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    display_name: Mapped[str] = mapped_column(String(255))
    arn: Mapped[str | None] = mapped_column(String(2048), default=None)
    attached_policies: Mapped[list[dict[str, str]] | None] = mapped_column(
        JSON, default=None
    )
    inline_policy_names: Mapped[list[str] | None] = mapped_column(JSON, default=None)
    # Members as identity provider identifiers, resolved within the
    # same file; membership is observed, never stored as state (D-006).
    member_identifiers: Mapped[list[str] | None] = mapped_column(JSON, default=None)


class PolicyDocumentRecord(Base):
    """A managed policy's default-version document as one snapshot saw it."""

    __tablename__ = "policy_documents"
    __table_args__ = (UniqueConstraint("snapshot_id", "policy_arn"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("snapshots.id"))
    policy_arn: Mapped[str] = mapped_column(String(2048))
    policy_name: Mapped[str] = mapped_column(String(255))
    aws_managed: Mapped[bool] = mapped_column(default=False)
    document: Mapped[dict[str, object] | None] = mapped_column(JSON, default=None)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # Attribution survives user deletion: the id may dangle, the
    # username snapshot stays readable.
    actor_user_id: Mapped[int | None] = mapped_column(default=None)
    actor_username: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    target: Mapped[str | None] = mapped_column(String(255), default=None)
    detail: Mapped[str | None] = mapped_column(String(1000), default=None)
    ip: Mapped[str | None] = mapped_column(String(64), default=None)
