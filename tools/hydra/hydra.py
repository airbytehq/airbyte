#!/usr/bin/env -S uv run --script
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27,<1"]
# ///
"""Prototype of the `hydra` CLI: compute a PR's Hydra state and publish it as a check run.

This is a demo of the shape of the tool, not the real implementation. It collects facts
from GitHub (one GraphQL query) and Devin (sessions linked from the PR), derives per-stage
state, decides a next action, and renders it as JSON, markdown, or a `Hydra State` check run.

Usage:
    tools/hydra/hydra.py status 87645                # markdown summary
    tools/hydra/hydra.py status 87645 --json         # machine-readable state
    tools/hydra/hydra.py facts 87645 > snap.json     # capture raw facts
    tools/hydra/hydra.py status 87645 --facts snap.json   # offline, no credentials
    tools/hydra/hydra.py publish 87645 --dry-run     # print the check run payload

Credentials:
    GitHub: `GITHUB_TOKEN`, else `gh auth token`.
    Devin (optional): `DEVIN_API_KEY` (or `DEVIN_AI_API_KEY` / `DEVIN_API_KEY_GLOBAL`) and
    `DEVIN_ORG_ID` (or `DEVIN_AI_ORG_ID`). The org is looked up via `/v3/self` if unset.
    Without a Devin key, state falls back to PR comment markers only.
    Publishing a check run needs `checks: write`, which only GitHub App tokens
    (including Actions' `GITHUB_TOKEN`) have; personal tokens cannot create check runs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import httpx


SCHEMA_VERSION = 1
CHECK_NAME = "Hydra State"
REPO = "airbytehq/airbyte"

# Playbook macro → pipeline stage. Sessions with other macros are listed but not staged.
MACRO_STAGES = {
    "!issue_fix": "fix",
    "!prove_fix": "prove",
    "!sonar_prove_it": "prove",
    "!pr_ai_review": "review",
    "!pr_scope_analysis": "ready",
    "!resolve_merge_conflicts": "conflicts",
}
STAGE_ORDER = ["fix", "prove", "review", "ready", "conflicts"]
MARKER_STAGES = {"prove_fix": "prove", "pr_ai_review": "review"}
PASSING = {"fix": {"FIX_PR_CREATED"}, "prove": {"PROVEN"}, "review": {"APPROVE"}, "ready": {"PASS"}}
TRUSTED_MARKER_AUTHORS = {"devin-ai-integration", "airbyte-support-bot"}
RUNNING_STATUSES = {"new", "claimed", "running", "resuming"}
# Checks that fail by design before a progressive rollout; they don't count as CI failures.
BENIGN_CHECK_PATTERNS = [
    re.compile(r"Progressive Rollout Gate$"),
    re.compile(r"^Connector Active Progressive Rollout Checks Summary$"),
    re.compile(r"^Suggest enabling autopilot rollouts$"),
]

MARKER_RE = re.compile(r"<!--\s*(?P<key>[a-z_]+?)_result:\s*(?P<value>[A-Za-z_]+)\s*;\s*head_sha:\s*(?P<sha>[0-9a-f]{7,40})\s*-->")
SESSION_LINK_RE = re.compile(r"app\.devin\.ai/sessions/([0-9a-f]{32})")

PR_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number title url state isDraft merged mergedAt createdAt body
      headRefOid headRefName baseRefName isCrossRepository mergeStateStatus
      author { login }
      labels(first: 50) { nodes { name } }
      assignees(first: 10) { nodes { login } }
      comments(last: 100) { nodes { author { login } body createdAt updatedAt url } }
      reviews(last: 50) { nodes { author { login } body state submittedAt commit { oid } } }
      commits(last: 1) { nodes { commit { oid committedDate statusCheckRollup {
        state
        contexts(first: 100) { nodes {
          __typename
          ... on CheckRun { name status conclusion }
          ... on StatusContext { context state }
        } }
      } } } }
    }
  }
}
"""


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------


def github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("No GitHub token: set GITHUB_TOKEN or run `gh auth login`.")


def devin_key() -> str | None:
    for var in ("DEVIN_API_KEY", "DEVIN_AI_API_KEY", "DEVIN_API_KEY_GLOBAL"):
        if os.environ.get(var):
            return os.environ[var]
    return None


def fetch_pr(number: int) -> dict:
    owner, name = REPO.split("/")
    resp = httpx.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {github_token()}"},
        json={"query": PR_QUERY, "variables": {"owner": owner, "name": name, "number": number}},
        timeout=60,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("errors"):
        sys.exit(f"GitHub GraphQL error: {payload['errors']}")
    return payload["data"]["repository"]["pullRequest"]


def fetch_devin_sessions(session_ids: list[str]) -> dict:
    """Return {"available": bool, "error": str|None, "sessions": [...]} for the linked sessions."""
    key = devin_key()
    if not key:
        return {"available": False, "error": "no Devin API key in environment", "sessions": []}
    headers = {"Authorization": f"Bearer {key}"}
    with httpx.Client(base_url="https://api.devin.ai/v3", headers=headers, timeout=60) as client:
        org = os.environ.get("DEVIN_ORG_ID") or os.environ.get("DEVIN_AI_ORG_ID")
        if not org:
            me = client.get("/self")
            if me.status_code != 200:
                return {"available": False, "error": f"/v3/self returned {me.status_code}", "sessions": []}
            org = me.json().get("org_id")
        playbooks = client.get(f"/organizations/{org}/playbooks", params={"first": 200})
        macros = {p["playbook_id"]: p.get("macro") for p in playbooks.json().get("items", [])} if playbooks.status_code == 200 else {}
        sessions = []
        for sid in session_ids:
            resp = client.get(f"/organizations/{org}/sessions/devin-{sid}")
            if resp.status_code != 200:
                sessions.append({"session_id": sid, "fetch_error": resp.status_code})
                continue
            s = resp.json()
            sessions.append(
                {
                    "session_id": sid,
                    "url": s.get("url"),
                    "status": s.get("status"),
                    "status_detail": s.get("status_detail"),
                    "macro": macros.get(s.get("playbook_id")),
                    "tags": s.get("tags") or [],
                    "created_at": s.get("created_at"),
                    "updated_at": s.get("updated_at"),
                    "is_archived": s.get("is_archived"),
                    "pull_requests": [p.get("pr_url") for p in s.get("pull_requests") or []],
                    "structured_output": s.get("structured_output"),
                }
            )
    return {"available": True, "error": None, "sessions": sessions}


def collect_facts(number: int) -> dict:
    pr = fetch_pr(number)
    texts = [pr.get("body") or ""] + [c["body"] for c in pr["comments"]["nodes"]] + [r["body"] or "" for r in pr["reviews"]["nodes"]]
    session_ids = sorted({m for t in texts for m in SESSION_LINK_RE.findall(t)})
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo": REPO,
        "pr": pr,
        "devin": fetch_devin_sessions(session_ids),
    }


# ---------------------------------------------------------------------------
# derive
# ---------------------------------------------------------------------------


def session_phase(s: dict) -> str:
    if s.get("fetch_error"):
        return "unknown"
    if s.get("status") in RUNNING_STATUSES:
        return "running"
    if s.get("status_detail") == "error":
        return "errored"
    if s.get("structured_output"):
        return "complete"
    if s.get("status_detail") == "waiting_for_user":
        return "waiting"
    return "ended_without_output"


def scope_gate(output: dict) -> tuple[str, list[str]]:
    """Deterministic version of hydra-automerge.yml's gate over pr_scope_analysis output."""
    pre = output.get("preconditions") or {}
    scope = output.get("change_scope") or {}
    failed = [k for k, v in pre.items() if not (isinstance(v, dict) and v.get("pass"))]
    scopes = [k for k, v in scope.items() if isinstance(v, dict) and v.get("pass")]
    reasons = [f"precondition failed: {k}" for k in failed]
    if not scopes:
        reasons.append("no allowed change scope matched")
    else:
        reasons.append("matched scope: " + ", ".join(scopes))
    return ("PASS" if not failed and scopes else "FAIL"), reasons


def result_from_output(stage: str, output: dict) -> tuple[str | None, str | None, list[str]]:
    """Return (verdict, head_sha, notes) from a stage's structured output."""
    if stage == "prove":
        return (output.get("verdict") or "").upper() or None, output.get("head_sha"), []
    if stage == "review":
        return output.get("decision"), output.get("head_sha"), []
    if stage == "fix":
        return (output.get("outcome") or "").upper() or None, (output.get("fix_pr") or {}).get("head_sha"), []
    if stage == "ready":
        verdict, reasons = scope_gate(output)
        return verdict, None, reasons + ["schema has no head_sha; freshness unknown"]
    return None, None, []


def latest_markers(pr: dict) -> dict:
    """Latest trusted result marker per stage, from the PR body and comments (edited comments included)."""
    found: dict = {}
    for c in sorted(pr["comments"]["nodes"], key=lambda c: c["updatedAt"]):
        author = ((c.get("author") or {}).get("login") or "").removesuffix("[bot]")
        for m in MARKER_RE.finditer(c["body"]):
            stage = MARKER_STAGES.get(m["key"])
            if not stage:
                continue
            found[stage] = {
                "verdict": m["value"].upper(),
                "head_sha": m["sha"],
                "author": author,
                "trusted": author in TRUSTED_MARKER_AUTHORS,
                "url": c["url"],
            }
    return found


def derive_state(facts: dict) -> dict:
    pr = facts["pr"]
    head = pr["headRefOid"]
    labels = sorted(l["name"] for l in pr["labels"]["nodes"])
    markers = latest_markers(pr)
    sessions = facts["devin"]["sessions"]

    by_stage: dict[str, list[dict]] = {}
    other_sessions = []
    for s in sessions:
        stage = MACRO_STAGES.get(s.get("macro") or "")
        (by_stage.setdefault(stage, []) if stage else other_sessions).append(s)

    stages = {}
    findings: list[str] = []
    for stage in STAGE_ORDER:
        runs = sorted(by_stage.get(stage, []), key=lambda s: s.get("created_at") or 0)
        marker = markers.get(stage)
        if not runs and not marker:
            continue
        entry: dict = {"runs": len(runs)}
        if runs:
            latest = runs[-1]
            phase = session_phase(latest)
            entry.update({"phase": phase, "session": latest.get("url"), "source": "devin_structured_output"})
            if latest.get("structured_output"):
                verdict, sha, notes = result_from_output(stage, latest["structured_output"])
                entry.update({"verdict": verdict, "head_sha": sha, "notes": notes})
        else:
            entry.update({"phase": "unknown", "source": "pr_marker"})
        if marker:
            entry["marker"] = {k: marker[k] for k in ("verdict", "head_sha", "trusted", "url")}
            if entry.get("verdict") is None:
                entry.update({"verdict": marker["verdict"], "head_sha": marker["head_sha"]})
                if runs:
                    entry["source"] = "pr_marker"
            elif (marker["verdict"], marker["head_sha"]) != (entry["verdict"], entry.get("head_sha")):
                findings.append(
                    f"{stage}: marker says {marker['verdict']}@{marker['head_sha'][:7]} but session output says "
                    f"{entry['verdict']}@{(entry.get('head_sha') or '?')[:7]}"
                )
            if not marker["trusted"]:
                findings.append(f"{stage}: marker written by untrusted author {marker['author']}")
        sha = entry.get("head_sha")
        entry["current"] = None if not sha else sha == head
        entry["passed"] = entry.get("verdict") in PASSING.get(stage, set()) if entry.get("verdict") else None
        stages[stage] = entry

    rollup = (pr["commits"]["nodes"][0]["commit"].get("statusCheckRollup") or {}) if pr["commits"]["nodes"] else {}
    failing, pending, benign = [], [], []
    for ctx in (rollup.get("contexts") or {}).get("nodes", []):
        name = ctx.get("name") or ctx.get("context") or "?"
        if name.startswith(CHECK_NAME):
            continue  # never count our own check
        conclusion = (ctx.get("conclusion") or ctx.get("state") or "").upper()
        if ctx.get("__typename") == "CheckRun" and ctx.get("status") != "COMPLETED":
            bucket = pending
        elif conclusion in {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "STARTUP_FAILURE", "ACTION_REQUIRED"}:
            bucket = benign if any(p.search(name) for p in BENIGN_CHECK_PATTERNS) else failing
        elif conclusion == "PENDING":
            bucket = pending
        else:
            continue
        if name not in bucket:
            bucket.append(name)

    is_hydra = pr["headRefName"].startswith("devin/") or any(l.startswith("hyd-") for l in labels) or bool(stages)
    state = {
        "schema_version": SCHEMA_VERSION,
        "repo": facts["repo"],
        "pr": pr["number"],
        "title": pr["title"],
        "url": pr["url"],
        "head_sha": head,
        "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "facts_collected_at": facts["collected_at"],
        "is_hydra_pr": is_hydra,
        "pr_state": "merged" if pr["merged"] else pr["state"].lower(),
        "draft": pr["isDraft"],
        "merge_state": pr["mergeStateStatus"],
        "labels": labels,
        "ci": {"failing": failing, "pending": pending, "expected_failures": benign},
        "stages": stages,
        "other_sessions": [{"macro": s.get("macro"), "phase": session_phase(s), "url": s.get("url")} for s in other_sessions],
        "sources": {"devin": "available" if facts["devin"]["available"] else f"unavailable ({facts['devin']['error']})"},
        "findings": findings,
    }
    state["current_stage"] = current_stage(state)
    state["next"] = decide(state)
    return state


def current_stage(state: dict) -> str:
    if state["pr_state"] == "merged":
        return "automerged" if "hyd-automerged" in state["labels"] else "merged"
    if state["pr_state"] == "closed":
        return "closed"
    reached = [s for s in ["fix", "prove", "review", "ready"] if s in state["stages"]]
    return reached[-1] if reached else "none"


# ---------------------------------------------------------------------------
# decide
# ---------------------------------------------------------------------------


def decide(state: dict) -> dict:
    """Simplified version of the hands-free decision tree. Returns the single next action and why."""
    stages, labels = state["stages"], state["labels"]

    def act(action: str, *reasons: str, blocked: bool = False) -> dict:
        return {"action": action, "reasons": list(reasons), "blocked": blocked}

    if state["pr_state"] != "open":
        return act("none", f"PR is {state['pr_state']}")
    if not state["is_hydra_pr"]:
        return act("none", "not a Hydra PR (no devin/ branch, hyd-* label, or Hydra session)")
    if "hyd-pause" in labels:
        return act("none", "hyd-pause label present", blocked=True)
    if "community" in labels:
        return act("none", "community PRs are excluded", blocked=True)
    running = [s for s, e in stages.items() if e.get("phase") == "running"]
    if running:
        return act("wait", f"{', '.join(running)} session still running")
    if state["merge_state"] == "DIRTY":
        return act("/ai-resolve-conflicts", "PR has merge conflicts")
    if state["ci"]["failing"]:
        return act("investigate-ci", "failing checks: " + ", ".join(state["ci"]["failing"][:5]), blocked=True)

    head = state["head_sha"][:7]
    for stage, command in (("prove", "/ai-prove-fix"), ("review", "/ai-review")):
        entry = stages.get(stage)
        if not entry or not entry.get("verdict"):
            return act(command, f"no {stage} verdict yet")
        if entry.get("phase") == "errored":
            return act("escalate", f"latest {stage} session errored", blocked=True)
        if entry["passed"] is False:
            return act("escalate", f"{stage} verdict is {entry['verdict']}", blocked=True)
        if entry["current"] is False:
            return act(command, f"{stage} verdict is for {entry['head_sha'][:7]}, head is {head}")

    ready = stages.get("ready")
    if not ready:
        return act("/ai-ready", "prove and review passed at head; auto-merge not yet evaluated")
    if ready.get("passed") is False:
        return act("human-review", "auto-merge gate failed: " + "; ".join(ready.get("notes") or []), blocked=True)
    if state["ci"]["pending"]:
        return act("wait", f"{len(state['ci']['pending'])} checks still running")
    return act("awaiting-merge", "all gates passed")


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------

PHASE_ICON = {"complete": "✅", "running": "⏳", "errored": "💥", "waiting": "💬", "ended_without_output": "❔", "unknown": "❔"}


def render_markdown(state: dict) -> str:
    nxt = state["next"]
    lines = [
        f"**Next:** `{nxt['action']}`" + (" (blocked)" if nxt["blocked"] else "") + f" — {'; '.join(nxt['reasons'])}",
        "",
        f"**PR:** [#{state['pr']}]({state['url']}) · {state['pr_state']}{' · draft' if state['draft'] else ''} · "
        f"head `{state['head_sha'][:7]}` · merge state `{state['merge_state']}` · current stage **{state['current_stage']}**",
        "",
    ]
    if state["stages"]:
        lines += ["| Stage | Session | Verdict | For commit | Current | Marker | Source |", "|---|---|---|---|---|---|---|"]
        for stage, e in state["stages"].items():
            session = f"[{PHASE_ICON.get(e['phase'], '')} {e['phase']}]({e['session']})" if e.get("session") else e["phase"]
            sha = f"`{e['head_sha'][:7]}`" if e.get("head_sha") else "—"
            current = {True: "✅", False: "⚠️ stale", None: "❔"}[e["current"]]
            marker = e.get("marker")
            marker_cell = f"[{marker['verdict']}@`{marker['head_sha'][:7]}`]({marker['url']})" if marker else "—"
            verdict = e.get("verdict") or "—"
            if e.get("passed") is True:
                verdict = f"✅ {verdict}"
            elif e.get("passed") is False:
                verdict = f"❌ {verdict}"
            lines.append(f"| {stage} | {session} | {verdict} | {sha} | {current} | {marker_cell} | {e['source']} |")
        lines.append("")
        notes = [f"- **{s}:** {n}" for s, e in state["stages"].items() for n in e.get("notes") or []]
        if notes:
            lines += ["**Notes**", *notes, ""]
    ci = state["ci"]
    lines.append(
        f"**CI:** {len(ci['failing'])} failing, {len(ci['pending'])} pending, {len(ci['expected_failures'])} expected pre-rollout failures"
        + (f" — failing: {', '.join(ci['failing'][:5])}" if ci["failing"] else "")
    )
    if state["findings"]:
        lines += ["", "**Findings**", *[f"- ⚠️ {f}" for f in state["findings"]]]
    if state["other_sessions"]:
        lines += ["", "**Other linked sessions:** " + ", ".join(f"[{s['macro'] or '?'}]({s['url']})" for s in state["other_sessions"])]
    lines += [
        "",
        f"<sub>labels: {', '.join(state['labels']) or 'none'} · devin: {state['sources']['devin']} · computed {state['computed_at']}</sub>",
    ]
    return "\n".join(lines)


def check_run_payload(state: dict, on_sha: str, name: str) -> dict:
    nxt = state["next"]
    stage_bits = []
    for stage, e in state["stages"].items():
        mark = "✓" if e.get("passed") and e.get("current") else ("stale" if e.get("current") is False else (e.get("verdict") or e["phase"]))
        stage_bits.append(f"{stage} {mark}")
    title = f"next: {nxt['action']}" + (" (blocked)" if nxt["blocked"] else "") + (" · " + " · ".join(stage_bits) if stage_bits else "")
    body = json.dumps(state, indent=2)
    return {
        "name": name,
        "head_sha": on_sha,
        "status": "completed",
        "conclusion": "neutral",
        "external_id": f"v{SCHEMA_VERSION}:{state['pr']}:{state['head_sha'][:12]}",
        "details_url": state["url"],
        "output": {
            "title": title[:250],
            "summary": render_markdown(state)[:65000],
            "text": f"<details><summary>Machine-readable state (schema v{SCHEMA_VERSION})</summary>\n\n```json\n{body[:64000]}\n```\n</details>",
        },
    }


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------


def load_facts(args: argparse.Namespace) -> dict:
    if args.facts:
        with open(args.facts) as f:
            return json.load(f)
    return collect_facts(args.pr)


def main() -> None:
    parser = argparse.ArgumentParser(prog="hydra", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("facts", "print raw facts as JSON"),
        ("status", "print derived state"),
        ("publish", "write the Hydra State check run"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("pr", type=int)
        p.add_argument("--facts", help="read facts from a snapshot file instead of the APIs")
        if name == "status":
            p.add_argument("--json", action="store_true", help="print state JSON instead of markdown")
        if name == "publish":
            p.add_argument("--on-sha", help="commit to attach the check to (default: the PR's head)")
            p.add_argument("--name", default=CHECK_NAME)
            p.add_argument("--dry-run", action="store_true", help="print the payload instead of posting")
    args = parser.parse_args()

    if args.command == "facts":
        print(json.dumps(collect_facts(args.pr), indent=2))
        return
    state = derive_state(load_facts(args))
    if args.command == "status":
        print(json.dumps(state, indent=2) if args.json else render_markdown(state))
        return
    payload = check_run_payload(state, args.on_sha or state["head_sha"], args.name)
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return
    resp = httpx.post(
        f"https://api.github.com/repos/{REPO}/check-runs",
        headers={"Authorization": f"Bearer {github_token()}", "Accept": "application/vnd.github+json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code >= 300:
        sys.exit(f"check run create failed: {resp.status_code} {resp.text[:300]}")
    print(f"{args.name}: {resp.json().get('html_url')}  [{payload['output']['title']}]")


if __name__ == "__main__":
    main()
