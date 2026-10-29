# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).parents[3]
WORKFLOW = yaml.safe_load((REPO_ROOT / ".github/workflows/hydra-pr-assignment.yml").read_text())
JOB = WORKFLOW["jobs"]["assign"]
STEPS = {step["name"]: step for step in JOB["steps"]}
PR = {
    "state": "open",
    "user": {"login": "devin-ai-integration[bot]"},
    "head": {"repo": {"full_name": "airbytehq/airbyte"}},
    "labels": [{"name": "hyd-fix"}],
    "assignees": [],
}
GH_STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_CALLS"
printf '%s' "$GH_RESPONSE"
exit "${GH_EXIT:-0}"
"""


def run_step(tmp_path: Path, name: str, response: object, exit_code: int = 0) -> tuple[subprocess.CompletedProcess, str, str]:
    gh = tmp_path / "gh"
    gh.write_text(GH_STUB)
    gh.chmod(0o755)
    output = tmp_path / "output"
    calls = tmp_path / "calls"
    output.write_text("")
    calls.write_text("")
    completed = subprocess.run(
        ["bash", "-e", "-c", STEPS[name]["run"]],
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "GH_RESPONSE": json.dumps(response),
            "GH_EXIT": str(exit_code),
            "GH_CALLS": str(calls),
            "GITHUB_OUTPUT": str(output),
            "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
            "GITHUB_REPOSITORY": "airbytehq/airbyte",
            "PR_NUMBER": "123",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    return completed, output.read_text(), calls.read_text()


def test_trigger_is_limited_to_initial_hydra_ownership() -> None:
    # PyYAML parses the YAML 1.1 key 'on' as True.
    assert WORKFLOW[True] == {"pull_request_target": {"types": ["opened", "labeled"]}}
    assert "github.event.pull_request.user.login == 'devin-ai-integration[bot]'" in JOB["if"]
    assert "github.event.sender.login == 'devin-ai-integration[bot]'" in JOB["if"]
    assert "github.event.pull_request.head.repo.full_name == github.repository" in JOB["if"]
    assert "github.event.label.name == 'hyd-fix'" in JOB["if"]
    assert "contains(github.event.pull_request.labels.*.name, 'hyd-fix')" in JOB["if"]
    assert STEPS["Preserve explicit ownership opt-outs"]["if"] == "steps.ownership.outputs.eligible == 'true'"
    assert STEPS["Assign and verify Hydra ownership"]["if"] == "steps.opt-out.outputs.allowed == 'true'"
    assert WORKFLOW["permissions"] == {}
    assert "concurrency" not in WORKFLOW
    assert JOB["concurrency"]["cancel-in-progress"] is False
    assert not any("checkout" in step.get("uses", "") for step in JOB["steps"])


@pytest.mark.parametrize(
    "changes,eligible",
    [
        ({}, True),
        ({"assignees": [{"login": "airbyte-support-bot"}]}, False),
        ({"assignees": [{"login": "human-owner"}]}, False),
        ({"state": "closed"}, False),
        ({"labels": []}, False),
        ({"user": {"login": "human-author"}}, False),
        ({"head": {"repo": {"full_name": "contributor/airbyte"}}}, False),
        ({"head": {"repo": None}}, False),
    ],
)
def test_current_ownership(tmp_path: Path, changes: dict, eligible: bool) -> None:
    completed, output, calls = run_step(tmp_path, "Check current PR ownership", {**PR, **changes})
    assert completed.returncode == 0, completed.stderr
    assert output == f"eligible={str(eligible).lower()}\n"
    assert calls == "api repos/airbytehq/airbyte/pulls/123\n"


@pytest.mark.parametrize(
    "timeline,allowed",
    [
        ([[]], True),
        ([[{"event": "assigned", "assignee": {"login": "airbyte-support-bot"}}]], True),
        ([[{"event": "unassigned", "assignee": {"login": "another-owner"}}]], True),
        ([[], [{"event": "unassigned", "assignee": {"login": "airbyte-support-bot"}}]], False),
    ],
)
def test_explicit_opt_out_across_all_pages(tmp_path: Path, timeline: list, allowed: bool) -> None:
    completed, output, calls = run_step(tmp_path, "Preserve explicit ownership opt-outs", timeline)
    assert completed.returncode == 0, completed.stderr
    assert output == f"allowed={str(allowed).lower()}\n"
    assert calls == "api repos/airbytehq/airbyte/issues/123/timeline --paginate --slurp\n"


@pytest.mark.parametrize("name", ["Check current PR ownership", "Preserve explicit ownership opt-outs"])
def test_read_errors_fail_closed(tmp_path: Path, name: str) -> None:
    completed, output, _ = run_step(tmp_path, name, {"message": "Forbidden"}, exit_code=1)
    assert completed.returncode != 0
    assert output == ""


@pytest.mark.parametrize("assigned", [True, False])
def test_assignment_verifies_api_response(tmp_path: Path, assigned: bool) -> None:
    response = {"assignees": [{"login": "airbyte-support-bot"}] if assigned else []}
    completed, _, calls = run_step(tmp_path, "Assign and verify Hydra ownership", response)
    assert (completed.returncode == 0) == assigned
    assert calls == "api --method POST repos/airbytehq/airbyte/issues/123/assignees -f assignees[]=airbyte-support-bot\n"
    if assigned:
        assert "Assigned airbyte-support-bot to PR #123." in (tmp_path / "summary").read_text()
    else:
        assert "::error::Could not assign airbyte-support-bot to PR #123." in completed.stdout


def test_assignment_api_failure_is_not_reported_as_success(tmp_path: Path) -> None:
    completed, _, _ = run_step(tmp_path, "Assign and verify Hydra ownership", {"message": "Forbidden"}, exit_code=1)
    assert completed.returncode != 0
    assert not (tmp_path / "summary").exists()


def test_scripts_do_not_interpolate_github_expressions() -> None:
    assert all("${{" not in step["run"] for step in JOB["steps"] if "run" in step)
