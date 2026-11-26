# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import subprocess
from pathlib import Path

import pytest
import yaml


WORKFLOW = Path(__file__).parents[2] / "workflows" / "ai-resolve-conflicts-command.yml"
STEPS = yaml.safe_load(WORKFLOW.read_text())["jobs"]["ai-resolve-conflicts"]["steps"]
HEAD_STEP = next(step for step in STEPS if step.get("id") == "pr-head")
DEVIN_STEP = next(step for step in STEPS if step["name"] == "Run AI Resolve Conflicts")


def capture(tmp_path: Path, gh_output: str) -> subprocess.CompletedProcess[str]:
    gh = tmp_path / "gh"
    gh.write_text(f'#!/bin/bash\nprintf "%s\\n" "$@" > "$GH_ARGS"\nprintf "%s\\n" "{gh_output}"\n')
    gh.chmod(0o755)
    outputs = tmp_path / "outputs"
    outputs.touch()
    return subprocess.run(
        ["bash", "-e", "-c", HEAD_STEP["run"]],
        capture_output=True,
        text=True,
        env={
            "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}",
            "GH_ARGS": str(tmp_path / "gh-args"),
            "GITHUB_OUTPUT": str(outputs),
            "PR_NUMBER": "123",
        },
    )


def test_tags_session_with_pr_head(tmp_path: Path) -> None:
    sha = "0123456789abcdef" * 2 + "01234567"
    completed = capture(tmp_path, sha)
    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "gh-args").read_text().splitlines() == [
        "pr",
        "view",
        "123",
        "--repo",
        "airbytehq/airbyte",
        "--json",
        "headRefOid",
        "--jq",
        ".headRefOid",
    ]
    assert (tmp_path / "outputs").read_text().splitlines() == [f"sha={sha}", "tag=hydra-sha-0123456789ab"]


@pytest.mark.parametrize("gh_output", ["", "null", "not-a-sha"])
def test_fails_without_a_head_sha(tmp_path: Path, gh_output: str) -> None:
    completed = capture(tmp_path, gh_output)
    assert completed.returncode != 0
    assert "Could not read the head SHA of PR #123" in completed.stdout
    assert (tmp_path / "outputs").read_text() == ""


def test_head_is_captured_before_session_and_tagged() -> None:
    assert STEPS.index(HEAD_STEP) < STEPS.index(DEVIN_STEP)
    assert "${{ steps.pr-head.outputs.tag }}" in DEVIN_STEP["with"]["tags"].splitlines()
