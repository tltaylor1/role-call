"use strict";
// The one rule this file exists to keep: every value from the API
// reaches the page through textContent or a text node, never through
// innerHTML. Imported files control identity names, tags, and policy
// text, so all of it is untrusted, and this page has no markup sink
// that attacker-influenced strings can reach. The token lives in a
// closure variable, never in localStorage, so it does not survive a
// tab close and is not readable by injected script from another origin.

let token = null;
let currentUser = null;

const $ = (id) => document.getElementById(id);
const show = (id) => $(id).hidden = false;
const hide = (id) => $(id).hidden = true;

// Build one table row from a spec of plain-text cells. Numbers and
// strings only; nothing here parses HTML.
function row(cells, onClick) {
  const tr = document.createElement("tr");
  for (const cell of cells) {
    const td = document.createElement("td");
    td.textContent = String(cell);
    tr.appendChild(td);
  }
  if (onClick) {
    tr.classList.add("clickable");
    tr.addEventListener("click", onClick);
  }
  return tr;
}

function tile(label, value, kind) {
  const div = document.createElement("div");
  div.className = "tile " + (kind || "");
  const v = document.createElement("span");
  v.className = "tile-value";
  v.textContent = String(value);
  const l = document.createElement("span");
  l.className = "tile-label";
  l.textContent = label;
  div.append(v, l);
  return div;
}

async function api(path, options) {
  const opts = options || {};
  opts.headers = Object.assign({}, opts.headers);
  if (token) opts.headers["Authorization"] = "Bearer " + token;
  const response = await fetch(path, opts);
  if (response.status === 401) {
    signOut();
    throw new Error("session ended");
  }
  return response;
}

async function signIn(username, password) {
  const response = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error("invalid credentials");
  const body = await response.json();
  token = body.token;
  currentUser = username;
  return body.role;
}

function signOut() {
  if (token) api("/auth/logout", { method: "POST" }).catch(() => {});
  token = null;
  currentUser = null;
  for (const id of ["inventory", "detail", "groups", "imports", "nav", "asof"]) hide(id);
  show("signin");
}

function switchView(view) {
  for (const id of ["inventory", "detail", "groups", "imports"]) hide(id);
  show(view);
}

async function loadInventory() {
  switchView("inventory");
  const rows = await (await api("/identities")).json();
  const counts = { critical: 0, warning: 0, notice: 0, quiet: 0 };
  for (const r of rows) {
    if (r.critical) counts.critical++;
    else if (r.warning) counts.warning++;
    else if (r.notice) counts.notice++;
    else counts.quiet++;
  }
  const dash = $("dashboard");
  dash.replaceChildren(
    tile("identities", rows.length),
    tile("critical", counts.critical, "critical"),
    tile("warning", counts.warning, "warning"),
    tile("notice", counts.notice, "notice"),
    tile("quiet", counts.quiet, "quiet"),
  );
  renderIdentities(rows);
  window._identities = rows;
}

function identityTier(r) {
  if (r.critical) return "critical";
  if (r.warning) return "warning";
  if (r.notice) return "notice";
  return "quiet";
}

function renderIdentities(rows) {
  const text = $("filter-text").value.toLowerCase();
  const type = $("filter-type").value;
  const tier = $("filter-tier").value;
  const tbody = $("identity-rows");
  tbody.replaceChildren();
  for (const r of rows) {
    if (text && !r.display_name.toLowerCase().includes(text)) continue;
    if (type && r.identity_type !== type) continue;
    if (tier && identityTier(r) !== tier) continue;
    const flags = r.name_reused ? "name reused" : "";
    const tr = row(
      [r.display_name, r.identity_type, r.account,
       r.critical, r.warning, r.notice, flags],
      () => loadDetail(r.id),
    );
    tr.classList.add("tier-" + identityTier(r));
    tbody.appendChild(tr);
  }
}

function fact(dl, label, value) {
  const dt = document.createElement("dt");
  dt.textContent = label;
  const dd = document.createElement("dd");
  dd.textContent = value === null || value === undefined ? "unknown" : String(value);
  dl.append(dt, dd);
}

async function loadDetail(id) {
  const d = await (await api("/identities/" + id)).json();
  switchView("detail");
  $("detail-name").textContent = d.display_name + "  (" + d.identity_type + ")";
  const facts = $("detail-facts");
  facts.replaceChildren();
  fact(facts, "account", d.account);
  fact(facts, "owner", d.owner);
  fact(facts, "provisional", d.provisional);
  fact(facts, "name reused", d.name_reused);
  fact(facts, "as of", d.as_of);
  fact(facts, "observed days", d.observed_days);
  fact(facts, "last activity", d.last_activity);

  const findings = $("detail-findings");
  findings.replaceChildren();
  if (!d.findings.length) {
    const li = document.createElement("li");
    li.textContent = "no findings";
    findings.appendChild(li);
  }
  for (const f of d.findings) {
    const li = document.createElement("li");
    li.className = "finding tier-" + f.tier;
    const tag = document.createElement("span");
    tag.className = "finding-tier";
    tag.textContent = f.tier + " / " + f.anchor;
    const body = document.createElement("span");
    body.textContent = f.explanation;
    li.append(tag, body);
    findings.appendChild(li);
  }

  const sources = $("detail-sources");
  sources.replaceChildren();
  if (!d.privilege_sources.length) {
    const li = document.createElement("li");
    li.textContent = "no privilege sources";
    sources.appendChild(li);
  }
  for (const s of d.privilege_sources) {
    const li = document.createElement("li");
    li.textContent = s;
    sources.appendChild(li);
  }

  const timeline = $("detail-timeline");
  timeline.replaceChildren();
  for (const o of d.timeline) {
    timeline.appendChild(row([o.captured_at, o.source, o.fields_present]));
  }
}

async function loadGroups() {
  switchView("groups");
  const rows = await (await api("/groups")).json();
  const tbody = $("group-rows");
  tbody.replaceChildren();
  for (const g of rows) {
    const summary = g.findings.map((f) => f.code).join(", ") || "none";
    tbody.appendChild(row(
      [g.name, g.account, g.members, g.privileged ? "yes" : "no", summary]));
  }
}

async function loadImports() {
  switchView("imports");
  const rows = await (await api("/imports")).json();
  const tbody = $("import-rows");
  tbody.replaceChildren();
  for (const s of rows) {
    tbody.appendChild(row(
      [s.account, s.source, s.captured_at, s.imported_at, s.row_count, s.skipped_count]));
  }
}

async function refreshAsOf() {
  const rows = await (await api("/imports")).json();
  const el = $("asof");
  if (!rows.length) { hide("asof"); return; }
  const newest = rows.map((s) => s.captured_at).sort().at(-1);
  el.textContent = "inventory as of " + newest;
  show("asof");
}

function enterApp(role) {
  hide("signin");
  show("nav");
  $("whoami").textContent = currentUser + " (" + role + ")";
  refreshAsOf();
  loadInventory();
}

$("signin-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const err = $("signin-error");
  err.hidden = true;
  try {
    const role = await signIn(form.get("username"), form.get("password"));
    e.target.reset();
    enterApp(role);
  } catch {
    // The server's generic message, never echoed input.
    err.textContent = "Sign in failed.";
    err.hidden = false;
  }
});

$("nav").addEventListener("click", (e) => {
  const view = e.target.dataset.view;
  if (view === "inventory") loadInventory();
  else if (view === "groups") loadGroups();
  else if (view === "imports") loadImports();
});
$("signout").addEventListener("click", signOut);
$("back").addEventListener("click", loadInventory);
for (const id of ["filter-text", "filter-type", "filter-tier"]) {
  $(id).addEventListener("input", () => renderIdentities(window._identities || []));
}

$("import-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const kind = form.get("kind");
  const body = new FormData();
  body.append("file", form.get("file"));
  body.append("captured_at", form.get("captured_at"));
  const result = $("import-result");
  result.hidden = false;
  result.textContent = "importing...";
  try {
    const response = await api("/imports/" + kind, { method: "POST", body });
    const data = await response.json();
    if (response.ok) {
      result.textContent = "imported " + data.observations + " observations, "
        + data.identities_new + " new, " + data.skipped_rows + " skipped";
      e.target.reset();
      loadImports();
      refreshAsOf();
    } else {
      // The server's message states a rule; it never contains file text.
      result.textContent = "rejected: " + data.detail;
    }
  } catch {
    result.textContent = "the import could not be completed";
  }
});
