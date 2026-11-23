# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import subprocess
from pathlib import Path

import pytest
import yaml


WORKFLOWS = Path(__file__).parents[2] / "workflows"
PRODUCER = yaml.safe_load((WORKFLOWS / "publish_connectors.yml").read_text())["jobs"]["publish_connectors"]["steps"]
CONSUMER = yaml.safe_load((WORKFLOWS / "publish-connector-registry-artifacts.yml").read_text())["jobs"]["publish"]["steps"]
STAGE = next(step["run"] for step in PRODUCER if step.get("name") == "Stage Registry Artifacts for Publishing")
RESOLVE = next(step["run"] for step in CONSUMER if step.get("id") == "resolve-vars")


@pytest.mark.parametrize(("docker_tag", "expected_status"), [("1.2.3-rc1", 0), ("../../elsewhere", 1)])
def test_publish_bundle_preserves_image_tag(tmp_path: Path, docker_tag: str, expected_status: int) -> None:
    connector = "source-faker"
    artifacts = tmp_path / "registry-artifacts" / connector
    artifacts.mkdir(parents=True)
    metadata = "data:\n  dockerImageTag: 1.2.3\n"
    (artifacts / "metadata.yaml").write_text(metadata)
    output = tmp_path / "github-output"
    output.touch()
    env = {**os.environ, "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output), "CONNECTOR": connector, "DOCKER_TAG": docker_tag}

    subprocess.run(["bash", "-eo", "pipefail", "-c", STAGE], cwd=tmp_path, env=env, check=True)
    result = subprocess.run(["bash", "-eo", "pipefail", "-c", RESOLVE], env=env, check=False)

    assert result.returncode == expected_status
    assert (tmp_path / "registry-publish" / "files" / "metadata.yaml").read_text() == metadata
    assert output.read_text() == (f"version={docker_tag}\n" if expected_status == 0 else "")


def test_blocked_connector_has_no_publish_bundle(tmp_path: Path) -> None:
    output = tmp_path / "github-output"
    output.touch()
    env = {**os.environ, "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output), "CONNECTOR": "source-faker"}

    subprocess.run(["bash", "-eo", "pipefail", "-c", RESOLVE], env=env, check=True)

    assert output.read_text() == ""
