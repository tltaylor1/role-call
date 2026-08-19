"""The role vocabulary and the route matrix, single source.

ROUTE_ROLES is the one data structure that answers "who may call what."
The route dependencies read it to enforce, and the tests read it to
verify, so the enforced matrix and the tested matrix cannot drift
apart. A route is either in this matrix, or named public here, or the
drift test fails the build.
"""

from enum import StrEnum


class Role(StrEnum):
    reviewer = "reviewer"
    operator = "operator"
    administrator = "administrator"


ALL_ROLES: frozenset[Role] = frozenset(Role)

# Key form: "METHOD /path", matching FastAPI's registered routes.
ROUTE_ROLES: dict[str, frozenset[Role]] = {
    "GET /auth/me": ALL_ROLES,
    "POST /auth/logout": ALL_ROLES,
    "GET /admin/users": frozenset({Role.administrator}),
    "POST /admin/users": frozenset({Role.administrator}),
    # Reviewers read; importing changes the record, so it is the
    # operator's and administrator's act.
    "POST /imports/credential-report": frozenset({Role.operator, Role.administrator}),
    "POST /imports/authorization-details": frozenset({Role.operator, Role.administrator}),
    "GET /imports": ALL_ROLES,
    "GET /identities": ALL_ROLES,
    "GET /identities/{identity_id}": ALL_ROLES,
    "GET /groups": ALL_ROLES,
    # Governance writes change the record, so owner, purpose, and flag
    # are the operator's and administrator's acts. Attestation is every
    # role's act, because "I looked and it is still needed" is exactly
    # what a reviewer is for.
    "POST /identities/{identity_id}/governance": frozenset(
        {Role.operator, Role.administrator}
    ),
    "POST /groups/{group_id}/governance": frozenset(
        {Role.operator, Role.administrator}
    ),
    "POST /identities/{identity_id}/attest": ALL_ROLES,
    "POST /groups/{group_id}/attest": ALL_ROLES,
    "DELETE /governance/{record_id}": frozenset(
        {Role.operator, Role.administrator}
    ),
}

# Routes that are reachable without a session, each with its reason.
PUBLIC_ROUTES: frozenset[str] = frozenset(
    {
        "POST /auth/login",  # the way in
        "GET /health",  # liveness for the platform
        "GET /health/database",  # readiness for the platform
        "GET /",  # the page shell, which carries no data
    }
)
