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
from rolecall.models import Account, Identity, Observation, Snapshot

router = APIRouter()


class IdentityView(BaseModel):
    id: int
    account: str
    display_name: str
    identity_type: str
    provisional: bool
    observations: int
    name_reused: bool
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
    findings: list[FindingView]
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
    views = []
    for identity, account in identities:
        mine = pairs.get(identity.id, [])
        tiers = {"critical": 0, "warning": 0, "notice": 0}
        if mine and identity.account_id in as_of_by_account:
            state = derive(mine, as_of_by_account[identity.account_id])
            state.identity_type = identity.identity_type
            for finding in evaluate(state):
                tiers[finding.tier] += 1
        views.append(IdentityView(
            id=identity.id,
            account=account,
            display_name=identity.first_display_name,
            identity_type=identity.identity_type,
            provisional=identity.provisional,
            observations=len(mine),
            name_reused=seen[(identity.account_id, identity.first_display_name)] > 1,
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
    reused = db.execute(
        select(func.count()).select_from(Identity).where(
            Identity.account_id == identity.account_id,
            Identity.first_display_name == identity.first_display_name,
        )
    ).scalar_one() > 1
    sources: dict[datetime, str] = {
        captured: source
        for captured, source in db.execute(
            select(Snapshot.captured_at, Snapshot.source)
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
        findings=[FindingView(**vars(f)) for f in findings],
        timeline=[
            ObservationView(
                captured_at=captured.isoformat(),
                source=str(sources.get(captured, "")),
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
