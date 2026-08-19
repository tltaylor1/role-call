"""The page: served, headed, and unable to render markup.

Imported files control identity names, tags, and policy text, so this
suite treats the page as the place that content finally lands. The
scan is a gate rather than a habit: a future edit that reaches for a
markup sink fails the build instead of a review.
"""

import re
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from rolecall.roles import Role
from tests.conftest import ROLE_USERS, auth_header, login, make_user
from tests.reportlib import HEADER

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

# Sinks that turn a string into markup or code. The page builds every
# element through the document interface instead, so none of these has
# a legitimate use here; a future one is a decision, not a detail.
FORBIDDEN_IN_SCRIPT = (
    "innerHTML", "outerHTML", "insertAdjacentHTML", "document.write",
    "eval(", "new Function(", "dangerouslySet",
)

PAYLOAD = '<img src=x onerror="alert(1)">'


def script_without_comments() -> str:
    """Comments may name the sinks they warn about; code may not."""
    lines = []
    for line in (FRONTEND / "app.js").read_text().splitlines():
        if line.strip().startswith("//"):
            continue
        lines.append(line)
    return "\n".join(lines)


def test_the_page_has_no_markup_sink() -> None:
    code = script_without_comments()
    for sink in FORBIDDEN_IN_SCRIPT:
        assert sink not in code, f"the page reaches for {sink}"


def test_the_markup_has_no_inline_script_or_handler() -> None:
    """The content policy forbids inline execution; this proves the
    page does not need it, so the policy can stay strict."""
    markup = (FRONTEND / "index.html").read_text()
    # A script element may reference a file; it may not carry code.
    inline = [
        body for body in re.findall(r"<script[^>]*>([\s\S]*?)</script>", markup)
        if body.strip()
    ]
    assert not inline, f"inline script block: {inline}"
    assert not re.search(r"\son[a-z]+\s*=", markup, re.I), "inline event handler"
    assert not re.search(r"\sstyle\s*=", markup, re.I), "inline style attribute"


def test_the_shell_is_served_with_its_headers(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    policy = response.headers["content-security-policy"]
    assert "default-src 'self'" in policy
    assert "'unsafe-inline'" not in policy
    assert "frame-ancestors 'none'" in policy
    assert response.headers["x-content-type-options"] == "nosniff"


def test_the_assets_are_served(client: TestClient) -> None:
    for path, kind in (("/static/app.js", "javascript"), ("/static/app.css", "css")):
        response = client.get(path)
        assert response.status_code == 200, path
        assert kind in response.headers["content-type"]


def test_api_responses_carry_the_headers_too(client: TestClient, db: Session) -> None:
    make_user(db, Role.reviewer)
    token = login(client, ROLE_USERS[Role.reviewer])
    response = client.get("/identities", headers=auth_header(token))
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "content-security-policy" in response.headers


def test_the_timeline_names_each_source_correctly(
    client: TestClient, db: Session
) -> None:
    """Both formats import at the same capture time, so a timeline
    keyed by time labels half the rows with the wrong source. Found by
    reading the rendered page, not by a passing test."""
    from rolecall.sample_data import GENERATIONS, file_set

    make_user(db, Role.operator)
    token = login(client, ROLE_USERS[Role.operator])
    files = file_set()
    captured = GENERATIONS[0]
    day = captured.strftime("%Y-%m-%d")
    for name, route in (
        (f"{day}-credential-report.csv", "credential-report"),
        (f"{day}-authorization-details.json", "authorization-details"),
    ):
        client.post(
            f"/imports/{route}",
            headers=auth_header(token),
            files={"file": (name, files[name].encode(), "text/plain")},
            data={"captured_at": captured.isoformat()},
        )
    rows = client.get("/identities", headers=auth_header(token)).json()
    target = [r for r in rows if r["display_name"] == "ci-deployer"][0]
    detail = client.get(
        f"/identities/{target['id']}", headers=auth_header(token)
    ).json()
    sources = {entry["source"] for entry in detail["timeline"]}
    assert sources == {"credential_report", "authorization_details"}


def test_hostile_names_survive_as_data_and_never_as_markup(
    client: TestClient, db: Session
) -> None:
    """The end-to-end canary: a name that is markup goes in through an
    import, comes back as a JSON string, and appears nowhere in the
    page the browser parses."""
    make_user(db, Role.operator)
    token = login(client, ROLE_USERS[Role.operator])
    report = (
        HEADER + "\n"
        + f"{PAYLOAD},arn:aws:iam::123456789012:user/hostile,"
        "2025-01-01T00:00:00+00:00,FALSE,N/A,N/A,N/A,FALSE,"
        "FALSE,N/A,N/A,N/A,N/A,FALSE,N/A,N/A,N/A,N/A,FALSE,N/A,FALSE,N/A\n"
    ).encode()
    created = client.post(
        "/imports/credential-report",
        headers=auth_header(token),
        files={"file": ("hostile.csv", report, "text/csv")},
        data={"captured_at": "2026-08-01T00:00:00+00:00"},
    )
    assert created.status_code == 201, created.text

    listed = client.get("/identities", headers=auth_header(token))
    assert "application/json" in listed.headers["content-type"]
    # The value is preserved exactly, because mangling data to make it
    # safe is how a tool starts lying about what it found.
    names = [row["display_name"] for row in listed.json()]
    assert PAYLOAD in names
    # And it is delivered as a JSON string, not as a document a browser
    # would parse as markup.
    assert "<img" not in listed.text or '"<img' in listed.text

    # The shell is static: nothing from the database is templated into it.
    shell = client.get("/")
    assert PAYLOAD not in shell.text
    assert "hostile" not in shell.text
