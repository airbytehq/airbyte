#!/usr/bin/env -S uv run --script --python 3.12
# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["pytest==8.*", "pyyaml==6.*"]
# ///
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


WORKFLOW = Path(__file__).parents[2] / "workflows" / "hydra-automerge.yml"
STEPS = yaml.safe_load(WORKFLOW.read_text())["jobs"]["evaluate-and-merge"]["steps"]
RESULT_STEP = next(step for step in STEPS if step["name"] == "Publish readiness result on evaluated head")
PENDING_STEP = next(step for step in STEPS if step["name"] == "Publish pending readiness status")
EVALUATED_SHA = "a" * 40
BASE_ENV = {
    "EVALUATED_SHA": EVALUATED_SHA,
    "GITHUB_SHA": "b" * 40,
    "GITHUB_SERVER_URL": "https://github.com",
    "GITHUB_REPOSITORY": "airbytehq/airbyte",
    "GITHUB_RUN_ID": "1234",
    "JOB_STATUS": "success",
    "VALID_PATHS": "true",
    "SUPPORT_BOT_ASSIGNED": "true",
    "NO_DESTINATION_CHANGES": "true",
    "NO_DATABASE_SOURCE_CHANGES": "true",
    "CHECKS_READY": "true",
    "EVAL_RESULT": "PASS",
    "STRUCTURED_OUTPUT": "",
    "DRY_RUN": "",
}


def publish(tmp_path: Path, script: str, overrides: dict[str, str]) -> tuple[list[str], str]:
    gh = tmp_path / "gh"
    gh.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$GH_ARGS"\ncat\n')
    gh.chmod(0o755)
    arguments = tmp_path / "gh-args"
    completed = subprocess.run(
        ["bash", "-e", "-c", script],
        input="",
        capture_output=True,
        check=True,
        text=True,
        env={
            "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}",
            "GH_ARGS": str(arguments),
            **BASE_ENV,
            **overrides,
        },
    )
    return arguments.read_text().splitlines(), completed.stdout


@pytest.mark.parametrize(
    ("overrides", "state", "description"),
    [
        ({}, "success", "PASS"),
        ({"DRY_RUN": "true"}, "success", "PASS (dry run)"),
        ({"VALID_PATHS": "false"}, "failure", "NOT_ELIGIBLE: allowed_paths"),
        ({"SUPPORT_BOT_ASSIGNED": "false"}, "failure", "NOT_ELIGIBLE: support_bot_assigned"),
        ({"NO_DESTINATION_CHANGES": "false"}, "failure", "NOT_ELIGIBLE: no_destination_changes"),
        ({"NO_DATABASE_SOURCE_CHANGES": "false"}, "failure", "NOT_ELIGIBLE: no_database_source_changes"),
        (
            {"SUPPORT_BOT_ASSIGNED": "false", "NO_DESTINATION_CHANGES": "false", "NO_DATABASE_SOURCE_CHANGES": "false"},
            "failure",
            "NOT_ELIGIBLE: support_bot_assigned, no_destination_changes, no_database_source_changes",
        ),
        ({"CHECKS_READY": "false"}, "failure", "BLOCKED: required_checks"),
        ({"JOB_STATUS": "failure"}, "error", "ERROR: evaluation failure"),
        ({"JOB_STATUS": "cancelled"}, "error", "ERROR: evaluation cancelled"),
        ({"EVAL_RESULT": ""}, "error", "ERROR: missing evaluation result"),
        (
            {
                "EVAL_RESULT": "FAIL",
                "STRUCTURED_OUTPUT": json.dumps({"preconditions": {"no_breaking_changes": {"pass": False}}}),
            },
            "failure",
            "FAIL: no_breaking_changes",
        ),
        (
            {
                "EVAL_RESULT": "FAIL",
                "STRUCTURED_OUTPUT": json.dumps({"preconditions": {"ai_review_passed": {"pass": False}}}),
            },
            "failure",
            "FAIL: ai_review_passed",
        ),
        (
            {
                "EVAL_RESULT": "FAIL",
                "STRUCTURED_OUTPUT": json.dumps({"preconditions": {"no_breaking_changes": {"pass": True}}}),
            },
            "failure",
            "FAIL: allowed_change_scope",
        ),
    ],
)
def test_readiness_result(tmp_path: Path, overrides: dict[str, str], state: str, description: str) -> None:
    arguments, payload = publish(tmp_path, RESULT_STEP["run"], overrides)
    assert arguments == ["api", "--method", "POST", f"repos/airbytehq/airbyte/statuses/{EVALUATED_SHA}", "--input", "-"]
    assert json.loads(payload) == {
        "context": "Hydra / ai-ready",
        "state": state,
        "description": description,
        "target_url": "https://github.com/airbytehq/airbyte/actions/runs/1234",
    }


def test_pending_status_uses_pr_head_not_workflow_sha(tmp_path: Path) -> None:
    arguments, _ = publish(tmp_path, PENDING_STEP["run"], {})
    assert f"repos/airbytehq/airbyte/statuses/{EVALUATED_SHA}" in arguments
    assert "state=pending" in arguments
    assert "context=Hydra / ai-ready" in arguments


@pytest.mark.parametrize("step_id", ["validate-paths", "verify-checks"])
def test_moved_head_aborts_before_evaluating_new_commit(step_id: str) -> None:
    step = next(step for step in STEPS if step.get("id") == step_id)
    script = step["with"]["script"]
    completed = subprocess.run(
        [
            "node",
            "--input-type=module",
            "-e",
            'const github = {rest: {pulls: {get: async () => ({data: {head: {sha: "new-head"}}})}}};\n' + script,
        ],
        capture_output=True,
        text=True,
        env={"PATH": os.environ["PATH"], "EVALUATED_SHA": EVALUATED_SHA, "PR_NUMBER": "123"},
    )
    assert completed.returncode != 0
    assert "PR head moved" in completed.stderr


def test_final_status_runs_after_errors_before_merge() -> None:
    assert RESULT_STEP["if"].startswith("always() &&")
    assert "steps.pre-check.outputs.state == 'OPEN'" in RESULT_STEP["if"]
    assert RESULT_STEP["env"]["EVALUATED_SHA"] == PENDING_STEP["env"]["EVALUATED_SHA"]
    merge_step = next(step for step in STEPS if step["name"] == "Mark draft PR as ready for review")
    assert STEPS.index(RESULT_STEP) < STEPS.index(merge_step)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
