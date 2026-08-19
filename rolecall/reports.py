"""Exports and the risk report: every value escaped at the exit.

Two escaping regimes, each matched to where the value lands. The CSV
export neutralizes spreadsheet formula injection, because a cell that
begins with an operator executes in the reader's spreadsheet with the
reader's permissions, and imported files control names and tags. The
HTML report renders through an engine that escapes by default, so
markup injection is removed as a class the way the ORM removes query
injection, rather than remembered call by call (D-040). JSON carries
raw values, because JSON is data and its consumers parse rather than
interpret.

Ranking comes from the engine's tiers and nowhere else: the report
orders by critical, then warning, then notice, then name, so the
report and the dashboard can never disagree about what matters most.
"""

import csv
import io
from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader, select_autoescape

from rolecall.assessment import AssessedGroup, AssessedIdentity

# A cell beginning with one of these executes as a formula in common
# spreadsheets; a leading tab or carriage return smuggles the same.
FORMULA_LEADERS = ("=", "+", "-", "@", "\t", "\r")


def csv_safe(value: object) -> str:
    text = "" if value is None else str(value)
    if text.startswith(FORMULA_LEADERS):
        return "'" + text
    return text


def identity_row(a: AssessedIdentity) -> dict[str, object]:
    tiers = a.tier_counts()
    return {
        "account": a.account,
        "name": a.identity.first_display_name,
        "type": a.identity.identity_type,
        "owner": a.owner.name if a.owner else None,
        "owner_type": a.owner.owner_type if a.owner else None,
        "owner_source": a.owner.source if a.owner else None,
        "flagged": a.flagged,
        "critical": tiers["critical"],
        "warning": tiers["warning"],
        "notice": tiers["notice"],
        "findings": [
            {"code": f.code, "tier": f.tier, "anchor": f.anchor,
             "explanation": f.explanation}
            for f in a.findings
        ],
        "privilege_sources": (
            [s.describe() for s in a.picture.sources] if a.picture else []
        ),
        "last_activity": (
            a.state.last_activity.isoformat()
            if a.state and a.state.last_activity
            else None
        ),
        "observed_days": a.state.observed_days if a.state else 0,
    }


def group_row(g: AssessedGroup) -> dict[str, object]:
    return {
        "account": g.account,
        "name": g.name,
        "members": g.members,
        "privileged": g.privileged,
        "owner": g.owner.name if g.owner else None,
        "flagged": g.flagged,
        "findings": [
            {"code": f.code, "tier": f.tier, "anchor": f.anchor,
             "explanation": f.explanation}
            for f in g.findings
        ],
    }


def _tier(row: dict[str, object], key: str) -> int:
    return cast(int, row[key])


def rank(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """The single-source ranking rule: tiers, then name."""
    return sorted(
        rows,
        key=lambda r: (
            -_tier(r, "critical"),
            -_tier(r, "warning"),
            -_tier(r, "notice"),
            str(r["name"]),
        ),
    )


CSV_COLUMNS = (
    "account", "name", "type", "owner", "owner_type", "owner_source",
    "flagged", "critical", "warning", "notice", "finding_codes",
    "privilege_sources", "last_activity", "observed_days",
)


def to_csv(rows: list[dict[str, object]]) -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for row in rank(rows):
        findings = cast(list[dict[str, str]], row["findings"])
        codes = ", ".join(f["code"] for f in findings)
        sources = "; ".join(cast(list[str], row["privilege_sources"]))
        writer.writerow([
            csv_safe(row["account"]),
            csv_safe(row["name"]),
            csv_safe(row["type"]),
            csv_safe(row["owner"]),
            csv_safe(row["owner_type"]),
            csv_safe(row["owner_source"]),
            csv_safe(row["flagged"]),
            row["critical"],
            row["warning"],
            row["notice"],
            csv_safe(codes),
            csv_safe(sources),
            csv_safe(row["last_activity"]),
            row["observed_days"],
        ])
    return out.getvalue()


_environment = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(default=True, default_for_string=True),
)


def render_report(
    identities: list[dict[str, object]],
    groups: list[dict[str, object]],
    as_of: str | None,
) -> str:
    tiles = {
        "identities": len(identities),
        "critical": sum(1 for r in identities if _tier(r, "critical") > 0),
        "warning": sum(
            1
            for r in identities
            if _tier(r, "critical") == 0 and _tier(r, "warning") > 0
        ),
        "quiet": sum(
            1
            for r in identities
            if _tier(r, "critical") == 0
            and _tier(r, "warning") == 0
            and _tier(r, "notice") == 0
        ),
    }
    template = _environment.get_template("report.html.j2")
    return template.render(
        identities=rank(identities),
        groups=groups,
        as_of=as_of,
        tiles=tiles,
    )
