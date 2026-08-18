"""The identity inventory, minimal until subphase 1.7.

Enough to see what an import produced: every identity with its type,
account, and how many snapshots have observed it. The full inventory,
its enrichment, and the derived state arrive with the engine.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rolecall.db import get_session
from rolecall.deps import require_roles
from rolecall.models import Account, Identity, Observation

router = APIRouter()


class IdentityView(BaseModel):
    account: str
    display_name: str
    identity_type: str
    provisional: bool
    observations: int
    # Derived at read (D-006): true when another identity in the same
    # account has carried this display name under a different provider
    # identifier, which is the resurrection signal (D-016).
    name_reused: bool


@router.get("/identities", dependencies=[require_roles("GET /identities")])
def list_identities(
    db: Annotated[Session, Depends(get_session)],
) -> list[IdentityView]:
    rows = db.execute(
        select(
            Identity,
            Account.provider_account_id,
            func.count(Observation.id),
        )
        .join(Account, Identity.account_id == Account.id)
        .join(Observation, Observation.identity_id == Identity.id, isouter=True)
        .group_by(Identity.id, Account.provider_account_id)
        .order_by(Account.provider_account_id, Identity.first_display_name)
    ).all()
    seen: dict[tuple[int, str], int] = {}
    for identity, _, _ in rows:
        key = (identity.account_id, identity.first_display_name)
        seen[key] = seen.get(key, 0) + 1
    return [
        IdentityView(
            account=account,
            display_name=identity.first_display_name,
            identity_type=identity.identity_type,
            provisional=identity.provisional,
            observations=count,
            name_reused=seen[(identity.account_id, identity.first_display_name)] > 1,
        )
        for identity, account, count in rows
    ]
