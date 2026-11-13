# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parents[3]
SCRIPT = Path("poe-tasks/build-and-publish-java-connectors-with-tag.sh")
REPOSITORY = "airbyte/custom-image-name"
DIGEST = "sha256:" + "a" * 64


@pytest.fixture
def publish_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "poe-tasks").mkdir()
    shutil.copy(REPO_ROOT / SCRIPT, tmp_path / SCRIPT)
    shutil.copytree(REPO_ROOT / "poe-tasks/lib", tmp_path / "poe-tasks/lib")
    connector = tmp_path / "airbyte-integrations/connectors/destination-test"
    connector.mkdir(parents=True)
    (connector / "metadata.yaml").write_text("data:\n  tags:\n    - language:java\n")
    commands = tmp_path / "commands"
    commands.touch()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    mocks = {
        "yq": f"""case "$2" in
  .data.dockerImageTag) echo "${{TEST_METADATA_VERSION:-1.2.3}}" ;;
  .data.dockerRepository) echo '{REPOSITORY}' ;;
esac
""",
        "curl": "echo \"${TEST_TAG_STATUS:-404}\"\n",
        "git": "echo abcdef0\n",
        "sleep": "exit 0\n",
        "docker": f"""echo "docker $*" >> "$TEST_COMMANDS"
case "$3" in
  inspect) echo '{DIGEST}'; exit "${{TEST_INSPECT_EXIT:-0}}" ;;
  create) exit "${{TEST_CREATE_EXIT:-0}}" ;;
  *) exit 1 ;;
esac
""",
    }
    for name, body in mocks.items():
        executable = bin_dir / name
        executable.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{body}")
        executable.chmod(0o755)
    gradlew = tmp_path / "gradlew"
    gradlew.write_text('#!/usr/bin/env bash\necho "gradle $*" >> "$TEST_COMMANDS"\nexit "${TEST_GRADLE_EXIT:-0}"\n')
    gradlew.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("TEST_COMMANDS", str(commands))
    monkeypatch.delenv("CONNECTOR_VERSION_TAG", raising=False)
    return tmp_path


def publish(root: Path, *args: str, **env: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--name", "destination-test", *args],
        cwd=root,
        env={**os.environ, **env},
        text=True,
        capture_output=True,
    )
    return result, (root / "commands").read_text().splitlines()


@pytest.mark.parametrize("tag_exists", [False, True])
@pytest.mark.parametrize("resolved_version", ["", "4.5.6"])
def test_stable_publish_updates_latest_by_digest(publish_root: Path, tag_exists: bool, resolved_version: str) -> None:
    result, commands = publish(
        publish_root,
        "--with-semver-suffix=none",
        "--publish",
        TEST_TAG_STATUS=("200" if tag_exists else "404"),
        CONNECTOR_VERSION_TAG=resolved_version,
    )
    assert result.returncode == 0, result.stderr
    version = resolved_version or "1.2.3"
    expected = []
    if not tag_exists:
        expected.append(
            f"gradle -Pdocker.publish -DciMode=true -Psbom=false -Pdocker.tag={version} "
            ":airbyte-integrations:connectors:destination-test:assemble"
        )
    expected.extend(
        [
            f"docker buildx imagetools inspect {REPOSITORY}:{version} --format {{{{.Manifest.Digest}}}}",
            f"docker buildx imagetools create --prefer-index=false --tag {REPOSITORY}:latest {REPOSITORY}@{DIGEST}",
        ]
    )
    assert commands == expected


@pytest.mark.parametrize("tag_exists", [False, True])
@pytest.mark.parametrize(
    "suffix,metadata_version,resolved_version,expected_version",
    [
        ("preview", "1.2.3", "", "1.2.3-preview.abcdef0"),
        ("rc", "1.2.3", "", "1.2.3-rc1"),
        ("none", "1.2.3-rc1", "", "1.2.3-rc1"),
        ("none", "1.2.3-rc1", "1.2.3", "1.2.3"),
        ("none", "1.2.3-preview.abcdef0", "1.2.3", "1.2.3"),
        ("none", "1.2.3", "1.2.3-rc2", "1.2.3-rc2"),
        ("none", "1.2.3", "1.2.3-preview.abcdef0", "1.2.3-preview.abcdef0"),
        ("preview", "1.2.3", "4.5.6", "4.5.6"),
        ("rc", "1.2.3", "4.5.6", "4.5.6"),
    ],
)
def test_prerelease_does_not_update_latest(
    publish_root: Path, tag_exists: bool, suffix: str, metadata_version: str, resolved_version: str, expected_version: str
) -> None:
    result, commands = publish(
        publish_root,
        f"--with-semver-suffix={suffix}",
        "--publish",
        TEST_TAG_STATUS=("200" if tag_exists else "404"),
        TEST_METADATA_VERSION=metadata_version,
        CONNECTOR_VERSION_TAG=resolved_version,
    )
    assert result.returncode == 0, result.stderr
    assert not any(command.startswith("docker ") for command in commands)
    if tag_exists:
        assert commands == []
    else:
        assert len(commands) == 1
        assert f"-Pdocker.tag={expected_version} " in commands[0]


def test_default_mode_is_preview(publish_root: Path) -> None:
    result, commands = publish(publish_root, "--publish")
    assert result.returncode == 0, result.stderr
    assert len(commands) == 1
    assert "-Pdocker.tag=1.2.3-preview.abcdef0 " in commands[0]


@pytest.mark.parametrize("suffix", ["none", "preview", "rc"])
def test_dry_run_does_not_publish(publish_root: Path, suffix: str) -> None:
    result, commands = publish(publish_root, f"--with-semver-suffix={suffix}")
    assert result.returncode == 0, result.stderr
    assert commands == []


@pytest.mark.parametrize(
    "failure,last_command",
    [
        ("TEST_GRADLE_EXIT", "gradle "),
        ("TEST_INSPECT_EXIT", "docker buildx imagetools inspect "),
        ("TEST_CREATE_EXIT", "docker buildx imagetools create "),
    ],
)
def test_publish_failure_is_not_swallowed(publish_root: Path, failure: str, last_command: str) -> None:
    result, commands = publish(publish_root, "--with-semver-suffix=none", "--publish", **{failure: "1"})
    assert result.returncode != 0
    assert commands[-1].startswith(last_command)


def test_registry_error_does_not_publish(publish_root: Path) -> None:
    result, commands = publish(publish_root, "--with-semver-suffix=none", "--publish", TEST_TAG_STATUS="500")
    assert result.returncode != 0
    assert commands == []


def test_non_jvm_connector_is_skipped(publish_root: Path) -> None:
    (publish_root / "airbyte-integrations/connectors/destination-test/metadata.yaml").write_text("data:\n  tags:\n    - language:python\n")
    result, commands = publish(publish_root, "--with-semver-suffix=none", "--publish")
    assert result.returncode == 0, result.stderr
    assert commands == []
    assert "only supports JVM connectors" in result.stdout
