"""The identity inventory, now with derived state and findings.

Everything here is computed at read from observations (D-006): the list
carries tier counts per identity, and the detail route walks the
observation timeline with every finding explaining itself. The as-of
time is the account's newest snapshot capture, never the wall clock.
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rolecall.db import get_session
from rolecall.deps import require_roles
from rolecall.derive import derive
from rolecall.findings import evaluate
from rolecall.governance import (
    active_owners_by_target,
    active_records,
    apply_owner_governance,
    record_history,
    resolve_owner,
)
from rolecall.models import (
    Account,
    GovernanceRecord,
    Group,
    GroupObservation,
    Identity,
    Observation,
    PolicyDocumentRecord,
    Snapshot,
)
from rolecall.privilege import (
    GroupFacts,
    PolicyIndex,
    evaluate_group,
    evaluate_privilege,
    membership_drift,
    read_identity_privilege,
)
from rolecall.routes.governance import RecordView, record_view

router = APIRouter()


class IdentityView(BaseModel):
    id: int
    account: str
    display_name: str
    identity_type: str
    provisional: bool
    observations: int
    name_reused: bool
    flagged: bool
    owner: str | None
    critical: int
    warning: int
    notice: int


class FindingView(BaseModel):
    code: str
    tier: str
    anchor: str
    explanation: str


class ObservationView(BaseModel):
    captured_at: str
    source: str
    fields_present: int


class IdentityDetail(BaseModel):
    id: int
    account: str
    display_name: str
    identity_type: str
    provisional: bool
    name_reused: bool
    as_of: str
    observed_days: int
    last_activity: str | None
    owner: str | None
    owner_type: str | None
    owner_source: str | None
    privilege_sources: list[str]
    findings: list[FindingView]
    governance: list[RecordView]
    timeline: list[ObservationView]


def _observation_pairs(
    db: Session, identity_ids: list[int]
) -> dict[int, list[tuple[Observation, datetime]]]:
    rows = db.execute(
        select(Observation, Snapshot.captured_at, Snapshot.source)
        .join(Snapshot, Observation.snapshot_id == Snapshot.id)
        .where(Observation.identity_id.in_(identity_ids))
    ).all()
    out: dict[int, list[tuple[Observation, datetime]]] = {}
    for obs, captured, _source in rows:
        out.setdefault(obs.identity_id, []).append((obs, captured))
    return out


def _privilege_context(
    db: Session, account_id: int
) -> tuple[PolicyIndex, dict[str, GroupFacts], dict[str, list[str]]]:
    """Policies and groups from the freshest snapshot carrying each,
    the same read-time rule the derivation engine uses for fields, plus
    the previous membership for drift."""
    index = PolicyIndex()
    doc_rows = db.execute(
        select(PolicyDocumentRecord, Snapshot.captured_at)
        .join(Snapshot, PolicyDocumentRecord.snapshot_id == Snapshot.id)
        .where(Snapshot.account_id == account_id)
    ).all()
    if doc_rows:
        newest = max(captured for _, captured in doc_rows)
        for record, captured in doc_rows:
            if captured != newest:
                continue
            if record.policy_arn.startswith("inline:"):
                owner, _, name = record.policy_arn[len("inline:"):].partition("#")
                index.inline.setdefault(owner, {})[name] = record.document
            else:
                index.managed[record.policy_arn] = record.document

    group_rows = db.execute(
        select(GroupObservation, Group, Snapshot.captured_at)
        .join(Group, GroupObservation.group_id == Group.id)
        .join(Snapshot, GroupObservation.snapshot_id == Snapshot.id)
        .where(Snapshot.account_id == account_id)
        .order_by(Snapshot.captured_at)
    ).all()
    groups: dict[str, GroupFacts] = {}
    previous_members: dict[str, list[str]] = {}
    if group_rows:
        captures = sorted({captured for _, _, captured in group_rows})
        newest = captures[-1]
        prior = captures[-2] if len(captures) > 1 else None
        for observation, _group, captured in group_rows:  # noqa: B007
            if captured == newest:
                groups[observation.display_name] = GroupFacts(
                    name=observation.display_name,
                    key=_group.provider_identifier,
                    attached=list(observation.attached_policies or []),
                    inline_names=list(observation.inline_policy_names or []),
                    members=list(observation.member_identifiers or []),
                )
            elif prior is not None and captured == prior:
                previous_members[observation.display_name] = list(
                    observation.member_identifiers or []
                )
    return index, groups, previous_members


@router.get("/identities", dependencies=[require_roles("GET /identities")])
def list_identities(
    db: Annotated[Session, Depends(get_session)],
) -> list[IdentityView]:
    identities = db.execute(
        select(Identity, Account.provider_account_id)
        .join(Account, Identity.account_id == Account.id)
        .order_by(Account.provider_account_id, Identity.first_display_name)
    ).all()
    as_of_by_account: dict[int, datetime] = {
        account_id: captured
        for account_id, captured in db.execute(
            select(Snapshot.account_id, func.max(Snapshot.captured_at))
            .group_by(Snapshot.account_id)
        ).all()
    }
    pairs = _observation_pairs(db, [i.id for i, _ in identities])
    seen: dict[tuple[int, str], int] = {}
    for identity, _ in identities:
        key = (identity.account_id, identity.first_display_name)
        seen[key] = seen.get(key, 0) + 1
    owners = active_owners_by_target(db, "identity")
    flagged_ids = {
        target_id
        for (target_id,) in db.execute(
            select(GovernanceRecord.target_id).where(
                GovernanceRecord.target_type == "identity",
                GovernanceRecord.kind == "flag",
                GovernanceRecord.cleared_at.is_(None),
            )
        ).all()
    }
    contexts: dict[int, tuple[PolicyIndex, dict[str, GroupFacts], dict[str, list[str]]]] = {}
    views = []
    for identity, account in identities:
        mine = pairs.get(identity.id, [])
        tiers = {"critical": 0, "warning": 0, "notice": 0}
        effective = resolve_owner(owners.get(identity.id), None)
        if mine and identity.account_id in as_of_by_account:
            state = derive(mine, as_of_by_account[identity.account_id])
            state.identity_type = identity.identity_type
            findings = evaluate(state)
            if identity.account_id not in contexts:
                contexts[identity.account_id] = _privilege_context(
                    db, identity.account_id
                )
            index, groups, _ = contexts[identity.account_id]
            picture = read_identity_privilege(
                identity_key=identity.provider_identifier,
                tags=state.tags,
                attached=state.attached_raw,
                group_names=state.group_names,
                trust_policy=state.trust_policy,
                account_id=account,
                index=index,
                groups=groups,
            )
            findings = findings + evaluate_privilege(picture)
            # The same adjustment the detail route makes, so the list
            # counts and the detail view cannot disagree.
            effective = resolve_owner(owners.get(identity.id), picture.owner)
            findings = apply_owner_governance(
                findings, effective, picture.owner, picture.combined.privileged
            )
            for finding in findings:
                tiers[finding.tier] += 1
        views.append(IdentityView(
            id=identity.id,
            account=account,
            display_name=identity.first_display_name,
            identity_type=identity.identity_type,
            provisional=identity.provisional,
            observations=len(mine),
            name_reused=seen[(identity.account_id, identity.first_display_name)] > 1,
            flagged=identity.id in flagged_ids,
            owner=effective.name if effective else None,
            critical=tiers["critical"],
            warning=tiers["warning"],
            notice=tiers["notice"],
        ))
    return views


@router.get(
    "/identities/{identity_id}",
    dependencies=[require_roles("GET /identities/{identity_id}")],
)
def identity_detail(
    identity_id: int, db: Annotated[Session, Depends(get_session)]
) -> IdentityDetail:
    row = db.execute(
        select(Identity, Account.provider_account_id)
        .join(Account, Identity.account_id == Account.id)
        .where(Identity.id == identity_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="no such identity")
    identity, account = row
    pairs = _observation_pairs(db, [identity.id])
    mine = sorted(pairs.get(identity.id, []), key=lambda p: p[1])
    if not mine:
        raise HTTPException(status_code=404, detail="no observations recorded")
    as_of = db.execute(
        select(func.max(Snapshot.captured_at))
        .where(Snapshot.account_id == identity.account_id)
    ).scalar_one()
    state = derive(mine, as_of)
    state.identity_type = identity.identity_type
    findings = evaluate(state)
    index, groups, _ = _privilege_context(db, identity.account_id)
    picture = read_identity_privilege(
        identity_key=identity.provider_identifier,
        tags=state.tags,
        attached=state.attached_raw,
        group_names=state.group_names,
        trust_policy=state.trust_policy,
        account_id=account,
        index=index,
        groups=groups,
    )
    findings = findings + evaluate_privilege(picture)
    assigned = next(
        (
            r
            for r in active_records(db, "identity", identity.id)
            if r.kind == "owner"
        ),
        None,
    )
    effective = resolve_owner(assigned, picture.owner)
    findings = apply_owner_governance(
        findings, effective, picture.owner, picture.combined.privileged
    )
    reused = db.execute(
        select(func.count()).select_from(Identity).where(
            Identity.account_id == identity.account_id,
            Identity.first_display_name == identity.first_display_name,
        )
    ).scalar_one() > 1
    # Keyed by snapshot, never by capture time: the two sources import
    # at the same instant, so a time-keyed lookup silently labels half
    # the timeline with the other source's name.
    sources: dict[int, str] = {
        snapshot_id: source
        for snapshot_id, source in db.execute(
            select(Snapshot.id, Snapshot.source)
            .where(Snapshot.account_id == identity.account_id)
        ).all()
    }
    return IdentityDetail(
        id=identity.id,
        account=account,
        display_name=identity.first_display_name,
        identity_type=identity.identity_type,
        provisional=identity.provisional,
        name_reused=reused,
        as_of=as_of.isoformat(),
        observed_days=state.observed_days,
        last_activity=(
            state.last_activity.isoformat() if state.last_activity else None
        ),
        owner=effective.name if effective else None,
        owner_type=effective.owner_type if effective else None,
        owner_source=effective.source if effective else None,
        privilege_sources=[source.describe() for source in picture.sources],
        findings=[FindingView(**vars(f)) for f in findings],
        governance=[
            record_view(r) for r in record_history(db, "identity", identity.id)
        ],
        timeline=[
            ObservationView(
                captured_at=captured.isoformat(),
                source=sources.get(obs.snapshot_id, ""),
                fields_present=sum(
                    1 for c in (
                        "password_enabled","mfa_active","key1_active",
                        "key2_active","trust_policy","tags",
                        "attached_policies","group_names",
                    ) if getattr(obs, c) is not None
                ),
            )
            for obs, captured in mine
        ],
    )


class GroupView(BaseModel):
    id: int | None
    account: str
    name: str
    members: int
    privileged: bool
    owner: str | None
    flagged: bool
    findings: list[FindingView]
    governance: list[RecordView]


@router.get("/groups", dependencies=[require_roles("GET /groups")])
def list_groups(db: Annotated[Session, Depends(get_session)]) -> list[GroupView]:
    """Groups as governed privilege sources (D-019): what each grants,
    who is in it, what changed since the previous snapshot, and who
    answers for it."""
    accounts = db.execute(select(Account)).scalars().all()
    owners = active_owners_by_target(db, "group")
    views: list[GroupView] = []
    for account in accounts:
        index, groups, previous = _privilege_context(db, account.id)
        ids = {
            g.provider_identifier: g.id
            for g in db.execute(
                select(Group).where(Group.account_id == account.id)
            ).scalars()
        }
        for name, facts in sorted(groups.items()):
            reading, findings = evaluate_group(facts, index)
            if name in previous:
                findings = findings + membership_drift(
                    name, previous[name], facts.members
                )
            group_id = ids.get(facts.key)
            records = (
                record_history(db, "group", group_id)
                if group_id is not None
                else []
            )
            effective = resolve_owner(
                owners.get(group_id) if group_id is not None else None, None
            )
            findings = apply_owner_governance(
                findings, effective, None, reading.privileged
            )
            views.append(GroupView(
                id=group_id,
                account=account.provider_account_id,
                name=name,
                members=len(facts.members),
                privileged=reading.privileged,
                owner=effective.name if effective else None,
                flagged=any(
                    r.kind == "flag" and r.cleared_at is None for r in records
                ),
                findings=[FindingView(**vars(f)) for f in findings],
                governance=[record_view(r) for r in records],
            ))
    return views
