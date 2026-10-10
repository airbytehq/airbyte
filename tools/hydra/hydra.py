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
      timelineItems(first: 250, itemTypes: [
        PULL_REQUEST_COMMIT, HEAD_REF_FORCE_PUSHED_EVENT, LABELED_EVENT, UNLABELED_EVENT,
        READY_FOR_REVIEW_EVENT, CONVERT_TO_DRAFT_EVENT, MERGED_EVENT, CLOSED_EVENT, REOPENED_EVENT
      ]) { nodes {
        __typename
        ... on PullRequestCommit { commit { oid committedDate messageHeadline } }
        ... on HeadRefForcePushedEvent { createdAt actor { login } afterCommit { oid } }
        ... on LabeledEvent { createdAt actor { login } label { name } }
        ... on UnlabeledEvent { createdAt actor { login } label { name } }
        ... on ReadyForReviewEvent { createdAt actor { login } }
        ... on ConvertToDraftEvent { createdAt actor { login } }
        ... on MergedEvent { createdAt actor { login } }
        ... on ClosedEvent { createdAt actor { login } }
        ... on ReopenedEvent { createdAt actor { login } }
      } }
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
                    "origin": s.get("origin"),
                    "user_id": s.get("user_id"),
                    "service_user_id": s.get("service_user_id"),
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


def iso(value: str | int | float | None) -> str | None:
    """Normalize GitHub ISO strings and Devin epoch seconds to `YYYY-MM-DDTHH:MM:SSZ`."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def all_markers(pr: dict) -> list[dict]:
    """Every result marker on the PR, oldest first (edited comments ordered by their last edit)."""
    found = []
    for c in sorted(pr["comments"]["nodes"], key=lambda c: c["updatedAt"]):
        author = ((c.get("author") or {}).get("login") or "").removesuffix("[bot]")
        for m in MARKER_RE.finditer(c["body"]):
            stage = MARKER_STAGES.get(m["key"])
            if stage:
                found.append(
                    {
                        "stage": stage,
                        "verdict": m["value"].upper(),
                        "head_sha": m["sha"],
                        "author": author,
                        "trusted": author in TRUSTED_MARKER_AUTHORS,
                        "url": c["url"],
                        "at": iso(c["updatedAt"]),
                    }
                )
    return found


def session_trigger(s: dict) -> str:
    """Best-effort description of what launched a session."""
    tags = s.get("tags") or []
    if "hydra-stage-handoff" in tags:
        return "hydra-stage-handoff workflow"
    if "gh-actions-trigger" in tags:
        return "GitHub workflow (slash command or label)"
    return {"slack": "Slack", "webapp": "Devin web app", "api": "Devin API"}.get(s.get("origin") or "", s.get("origin") or "unknown")


def build_runs(stage: str, sessions: list[dict], markers: list[dict], findings: list[str], pr: dict) -> list[dict]:
    """One entry per attempt at a stage: every linked session, plus markers no session accounts for."""
    runs = []
    unmatched = list(markers)
    for n, s in enumerate(sorted(sessions, key=lambda s: s.get("created_at") or 0), start=1):
        run = {
            "attempt": n,
            "source": "devin_structured_output",
            "session": s.get("url"),
            "trigger": session_trigger(s),
            "started_at": iso(s.get("created_at")),
            "phase": session_phase(s),
            "verdict": None,
            "head_sha": None,
            "concluded_at": None,
            "concluded_at_source": None,
            "notes": [],
        }
        output = s.get("structured_output")
        if output:
            run["verdict"], run["head_sha"], run["notes"] = result_from_output(stage, output)
            match = next((m for m in unmatched if m["head_sha"] == run["head_sha"] and m["verdict"] == run["verdict"]), None)
            if match:
                unmatched.remove(match)
                run["marker"] = {k: match[k] for k in ("verdict", "head_sha", "trusted", "url")}
            # When the verdict landed: the output's own timestamp, else the matching marker comment, else last activity.
            if output.get("timestamp"):
                run["concluded_at"], run["concluded_at_source"] = iso(output["timestamp"]), "structured_output.timestamp"
            elif stage == "fix" and (output.get("fix_pr") or {}).get("url") == pr["url"]:
                # Fix sessions keep iterating on the PR they open, so last activity says nothing; the PR's creation does.
                run["concluded_at"], run["concluded_at_source"] = iso(pr["createdAt"]), "pr_opened"
            elif match:
                run["concluded_at"], run["concluded_at_source"] = match["at"], "marker_comment"
            else:
                run["concluded_at"], run["concluded_at_source"] = iso(s.get("updated_at")), "session_last_activity"
        elif run["phase"] in {"errored", "ended_without_output"}:
            run["concluded_at"], run["concluded_at_source"] = iso(s.get("updated_at")), "session_last_activity"
        runs.append(run)
    for m in unmatched:
        # A marker with no matching session: either the session wasn't linked from the PR, or it disagrees.
        latest_with_output = next((r for r in reversed(runs) if r["verdict"]), None)
        if latest_with_output and latest_with_output["head_sha"] == m["head_sha"]:
            findings.append(
                f"{stage}: marker says {m['verdict']}@{m['head_sha'][:7]} but session output says "
                f"{latest_with_output['verdict']}@{m['head_sha'][:7]}"
            )
            continue
        runs.append(
            {
                "attempt": None,
                "source": "pr_marker",
                "session": None,
                "trigger": "unknown (session not linked from PR)",
                "started_at": None,
                "phase": "unknown",
                "verdict": m["verdict"],
                "head_sha": m["head_sha"],
                "concluded_at": m["at"],
                "concluded_at_source": "marker_comment",
                "marker": {k: m[k] for k in ("verdict", "head_sha", "trusted", "url")},
                "notes": [],
            }
        )
    for m in markers:
        if not m["trusted"]:
            findings.append(f"{stage}: marker written by untrusted author {m['author']}")
    runs.sort(key=lambda r: r["concluded_at"] or r["started_at"] or "")
    for n, r in enumerate(runs, start=1):
        r["attempt"] = n
    return runs


def build_timeline(pr: dict, runs_by_stage: dict[str, list[dict]], other_sessions: list[dict]) -> list[dict]:
    """GitHub events and session starts/conclusions in time order."""
    events = [{"at": iso(pr["createdAt"]), "kind": "pr_opened", "detail": f"opened by {(pr.get('author') or {}).get('login')}"}]
    for item in pr["timelineItems"]["nodes"]:
        kind = item["__typename"]
        actor = (item.get("actor") or {}).get("login")
        if kind == "PullRequestCommit":
            c = item["commit"]
            events.append({"at": iso(c["committedDate"]), "kind": "commit", "sha": c["oid"], "detail": c["messageHeadline"]})
        elif kind == "HeadRefForcePushedEvent" and item.get("afterCommit"):
            events.append({"at": iso(item["createdAt"]), "kind": "force_push", "sha": item["afterCommit"]["oid"], "detail": f"by {actor}"})
        elif kind in {"LabeledEvent", "UnlabeledEvent"}:
            name = item["label"]["name"]
            if name.startswith("hyd-") or name in {"community", "auto-merge", "auto-ai-review"}:
                verb = "added" if kind == "LabeledEvent" else "removed"
                events.append({"at": iso(item["createdAt"]), "kind": f"label_{verb}", "detail": f"{name} by {actor}"})
        else:
            kind_name = re.sub(r"(?<!^)(?=[A-Z])", "_", kind.removesuffix("Event")).lower()
            events.append({"at": iso(item["createdAt"]), "kind": kind_name, "detail": f"by {actor}"})
    for c in pr["comments"]["nodes"]:
        command = re.match(r"\s*(/[a-z][a-z0-9-]*)", c["body"])
        if command:
            author = (c.get("author") or {}).get("login")
            events.append({"at": iso(c["createdAt"]), "kind": "command", "detail": f"{command[1]} by {author}", "url": c["url"]})
    for stage, runs in runs_by_stage.items():
        for r in runs:
            if r["started_at"]:
                events.append(
                    {"at": r["started_at"], "kind": "session_started", "stage": stage, "attempt": r["attempt"], "detail": r["trigger"], "url": r["session"]}
                )
            if r["concluded_at"]:
                result = f"{r['verdict']}@{r['head_sha'][:7]}" if r["verdict"] and r["head_sha"] else (r["verdict"] or r["phase"])
                events.append(
                    {
                        "at": r["concluded_at"],
                        "kind": "session_concluded" if r["session"] else "marker_posted",
                        "stage": stage,
                        "attempt": r["attempt"],
                        "detail": result,
                        "url": r["session"] or (r.get("marker") or {}).get("url"),
                    }
                )
    for s in other_sessions:
        events.append({"at": iso(s.get("created_at")), "kind": "session_started", "stage": None, "detail": s.get("macro") or "?", "url": s.get("url")})
    return sorted((e for e in events if e["at"]), key=lambda e: e["at"])


def build_transitions(timeline: list[dict], runs_by_stage: dict[str, list[dict]]) -> list[dict]:
    """Replay the timeline and record each change to a stage's status and to the overall current stage."""
    status: dict[str, tuple[str, str | None]] = {}  # stage -> (label, sha)
    head = None
    furthest = "none"
    pr_status = "open"
    transitions = []

    def record(at: str, subject: str, before: str, after: str, cause: str) -> None:
        if before != after:
            transitions.append({"at": at, "subject": subject, "from": before, "to": after, "cause": cause})

    for e in timeline:
        if e["kind"] in {"commit", "force_push"}:
            head = e["sha"]
            for stage, (label, sha) in list(status.items()):
                if sha and sha != head and not label.endswith("(stale)"):
                    stale = f"{label} (stale)"
                    status[stage] = (stale, sha)
                    record(e["at"], stage, label, stale, f"head moved to {head[:7]}")
        elif e["kind"] in {"session_concluded", "marker_posted"} and e.get("stage"):
            run = next(r for r in runs_by_stage[e["stage"]] if r["attempt"] == e["attempt"])
            # A fix's result is "the PR exists", not a judgment about one commit, so it never goes stale.
            sha = None if e["stage"] == "fix" else run["head_sha"]
            label = (run["verdict"] or run["phase"]) if e["stage"] == "fix" else e["detail"]
            label += " (stale)" if sha and head and sha != head else ""
            before = status.get(e["stage"], ("not run", None))[0]
            status[e["stage"]] = (label, sha)
            cause = f"attempt #{e['attempt']}" + (" (re-run)" if e["attempt"] > 1 else "")
            record(e["at"], e["stage"], before, label, cause)
            reached = [s for s in ["fix", "prove", "review", "ready"] if s in status]
            if reached and reached[-1] != furthest:
                record(e["at"], "current_stage", furthest, reached[-1], f"{e['stage']} attempt #{e['attempt']} concluded")
                furthest = reached[-1]
        elif e["kind"] in {"merged", "closed", "reopened"}:
            if e["kind"] == "closed" and pr_status == "merged":
                continue  # GitHub records a close alongside every merge
            after = "open" if e["kind"] == "reopened" else e["kind"]
            record(e["at"], "pr", pr_status, after, e["detail"])
            pr_status = after
    return transitions


def derive_state(facts: dict) -> dict:
    pr = facts["pr"]
    head = pr["headRefOid"]
    labels = sorted(l["name"] for l in pr["labels"]["nodes"])
    markers = all_markers(pr)
    sessions = facts["devin"]["sessions"]

    by_stage: dict[str, list[dict]] = {}
    other_sessions = []
    for s in sessions:
        stage = MACRO_STAGES.get(s.get("macro") or "")
        (by_stage.setdefault(stage, []) if stage else other_sessions).append(s)

    stages = {}
    runs_by_stage = {}
    findings: list[str] = []
    for stage in STAGE_ORDER:
        stage_markers = [m for m in markers if m["stage"] == stage]
        runs = build_runs(stage, by_stage.get(stage, []), stage_markers, findings, pr)
        if not runs:
            continue
        runs_by_stage[stage] = runs
        # The stage's current result is the latest run that produced a verdict; its phase is the latest run's.
        decisive = next((r for r in reversed(runs) if r["verdict"]), runs[-1])
        latest = runs[-1]
        entry = {
            "phase": latest["phase"],
            "verdict": decisive["verdict"],
            "head_sha": decisive["head_sha"],
            "session": decisive["session"],
            "source": decisive["source"],
            "notes": decisive["notes"],
            "attempts": len(runs),
        }
        if decisive.get("marker"):
            entry["marker"] = decisive["marker"]
        sha = entry["head_sha"]
        entry["current"] = None if not sha else sha == head
        entry["passed"] = entry["verdict"] in PASSING.get(stage, set()) if entry["verdict"] else None
        entry["runs"] = runs
        stages[stage] = entry
    timeline = build_timeline(pr, runs_by_stage, other_sessions)
    transitions = build_transitions(timeline, runs_by_stage)

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
        "transitions": transitions,
        "timeline": timeline,
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
        lines += ["| Stage | Attempts | Session | Verdict | For commit | Current | Marker | Source |", "|---|---|---|---|---|---|---|---|"]
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
            lines.append(f"| {stage} | {e['attempts']} | {session} | {verdict} | {sha} | {current} | {marker_cell} | {e['source']} |")
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
    lines += render_history(state)
    lines += [
        "",
        f"<sub>labels: {', '.join(state['labels']) or 'none'} · devin: {state['sources']['devin']} · computed {state['computed_at']}</sub>",
    ]
    return "\n".join(lines)


TIMELINE_ICON = {
    "pr_opened": "🆕",
    "commit": "⬆️",
    "force_push": "⏫",
    "command": "💬",
    "session_started": "▶️",
    "session_concluded": "🏁",
    "marker_posted": "🏷️",
    "label_added": "➕",
    "label_removed": "➖",
    "ready_for_review": "👀",
    "convert_to_draft": "📝",
    "merged": "🟣",
    "closed": "⛔",
    "reopened": "🔄",
}


def short_time(at: str) -> str:
    return at[5:16].replace("T", " ")  # MM-DD HH:MM (UTC)


def link(text: str, url: str | None) -> str:
    return f"[{text}]({url})" if url else text


def render_history(state: dict) -> list[str]:
    lines = []
    if state["transitions"]:
        lines += ["", "**State transitions** (UTC)", "", "| When | What | From | To | Why |", "|---|---|---|---|---|"]
        for t in state["transitions"]:
            lines.append(f"| {short_time(t['at'])} | {t['subject']} | {t['from']} | **{t['to']}** | {t['cause']} |")
    runs = [(stage, r) for stage, e in state["stages"].items() for r in e["runs"]]
    if runs:
        lines += ["", f"<details><summary><b>Attempts per stage</b> ({len(runs)})</summary>", ""]
        lines += ["| Stage | # | Trigger | Started | Concluded | Result | Session |", "|---|---|---|---|---|---|---|"]
        for stage, r in runs:
            result = f"{r['verdict'] or r['phase']}" + (f"@`{r['head_sha'][:7]}`" if r["head_sha"] else "")
            concluded = short_time(r["concluded_at"]) + (" ≈" if r["concluded_at_source"] == "session_last_activity" else "") if r["concluded_at"] else "—"
            started = short_time(r["started_at"]) if r["started_at"] else "—"
            session = link("session", r["session"]) if r["session"] else link("marker only", (r.get("marker") or {}).get("url"))
            lines.append(f"| {stage} | {r['attempt']} | {r['trigger']} | {started} | {concluded} | {result} | {session} |")
        lines += ["", "<sub>≈ = conclusion time approximated from the session's last activity</sub>", "", "</details>"]
    if state["timeline"]:
        lines += ["", f"<details><summary><b>Timeline</b> ({len(state['timeline'])} events)</summary>", ""]
        for e in state["timeline"]:
            subject = f"{e['stage']} #{e['attempt']}: " if e.get("stage") and e.get("attempt") else ""
            sha = f" `{e['sha'][:7]}`" if e.get("sha") else ""
            text = f"{e['kind'].replace('_', ' ')}{sha} — {subject}{e['detail']}"
            lines.append(f"- `{short_time(e['at'])}` {TIMELINE_ICON.get(e['kind'], '•')} {link(text, e.get('url'))}")
        lines += ["", "<sub>commit times are commit dates, which can predate the push</sub>", "", "</details>"]
    return lines


def state_json_for_check(state: dict, limit: int = 60000) -> str:
    """Serialize state for the check run, dropping the bulkiest history first so the JSON stays valid."""
    body = json.dumps(state, indent=2)
    if len(body) <= limit:
        return body
    trimmed = {**state, "timeline": [], "truncated": ["timeline"]}
    body = json.dumps(trimmed, indent=2)
    if len(body) <= limit:
        return body
    trimmed["stages"] = {k: {**v, "runs": v["runs"][-3:]} for k, v in state["stages"].items()}
    trimmed["truncated"].append("stages.*.runs (kept last 3)")
    return json.dumps(trimmed, indent=2)


def check_run_payload(state: dict, on_sha: str, name: str) -> dict:
    nxt = state["next"]
    stage_bits = []
    for stage, e in state["stages"].items():
        mark = "✓" if e.get("passed") and e.get("current") else ("stale" if e.get("current") is False else (e.get("verdict") or e["phase"]))
        stage_bits.append(f"{stage} {mark}")
    title = f"next: {nxt['action']}" + (" (blocked)" if nxt["blocked"] else "") + (" · " + " · ".join(stage_bits) if stage_bits else "")
    body = state_json_for_check(state)
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
            "text": f"<details><summary>Machine-readable state (schema v{SCHEMA_VERSION})</summary>\n\n```json\n{body}\n```\n</details>",
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
