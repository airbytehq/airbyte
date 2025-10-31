#!/usr/bin/env -S uv run --python 3.12 --script
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
# /// script
# requires-python = "==3.12"
# dependencies = []
# ///

"""
Generate GitHub Actions matrix for modified Airbyte connectors.

This module detects which connectors have been modified and generates
a matrix configuration for GitHub Actions that includes language detection
and runner type selection.

Functions are designed to be called by poethepoet script tasks.

Usage
-----
Run doctests to verify utility functions:

    ./poe-tasks/connector_matrix.py --run-tests

List modified connectors (regular git detection):

    poe get-modified-connectors --json

List modified connectors with custom file list override:

    poe get-modified-connectors --json --files-list "airbyte-integrations/connectors/source-faker/setup.py,airbyte-integrations/connectors/destination-bigquery/build.gradle"

Generate enhanced matrix for GitHub Actions (regular git detection):

    poe generate-connector-matrix airbytehq/airbyte

Generate enhanced matrix with custom file list override:

    poe generate-connector-matrix airbytehq/airbyte --files-list "airbyte-integrations/connectors/source-faker/setup.py"

Testing
-------
This module includes doctests for key utility functions. To run the tests:

    cd ~/repos/airbyte
    python -m doctest poe-tasks/connector_matrix.py -v

All tests should pass. The doctests demonstrate expected behavior for:
- CSV file list parsing
- File filtering based on ignore patterns
- Connector path extraction
- Empty matrix format
- Output formatting (JSON vs text)
"""

import doctest
import json
import re
import subprocess
import sys
from pathlib import Path


DEFAULT_BRANCH = "master"
CONNECTORS_DIR = Path("airbyte-integrations/connectors")
IGNORE_PATTERNS = [
    ".coveragerc",
    "poe_tasks.toml",
    "README.md",
]


def get_git_remote() -> str:
    """Determine the correct git remote (upstream or origin)."""
    try:
        subprocess.run(
            ["git", "remote", "get-url", "upstream"],
            check=True,
            capture_output=True,
        )
        return "upstream"
    except subprocess.CalledProcessError:
        return "origin"


def get_modified_files(prev_commit: bool = False, files_list: str | None = None) -> list[str]:
    """Get list of modified files using git or from provided CSV string.

    >>> get_modified_files(files_list="file1.py, file2.txt,file3.md")
    ['file1.py', 'file2.txt', 'file3.md']
    >>> get_modified_files(files_list="  spaced.py  ,  another.txt  ")
    ['spaced.py', 'another.txt']
    >>> get_modified_files(files_list="")
    []
    """
    if files_list is not None:
        files = [f.strip() for f in files_list.split(",") if f.strip()]
        return files

    remote = get_git_remote()

    subprocess.run(
        ["git", "fetch", "--quiet", remote, DEFAULT_BRANCH],
        check=True,
    )

    if prev_commit:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = result.stdout.strip().split("\n")
    else:
        committed = (
            subprocess.run(
                ["git", "diff", "--name-only", f"{remote}/{DEFAULT_BRANCH}...HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .split("\n")
        )

        staged = (
            subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .split("\n")
        )

        unstaged = (
            subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .split("\n")
        )

        untracked = (
            subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .split("\n")
        )

        files = committed + staged + unstaged + untracked

    return [f for f in files if f]


def filter_ignored_files(files: list[str]) -> list[str]:
    """Filter out files matching ignore patterns.

    >>> filter_ignored_files(["airbyte-integrations/connectors/source-faker/setup.py"])
    ['airbyte-integrations/connectors/source-faker/setup.py']
    >>> filter_ignored_files(["airbyte-integrations/connectors/source-faker/README.md"])
    []
    >>> filter_ignored_files(["airbyte-integrations/connectors/source-faker/poe_tasks.toml"])
    []
    >>> filter_ignored_files(["some/path/.coveragerc"])
    []
    """
    ignore_regex = "|".join(re.escape(pattern) for pattern in IGNORE_PATTERNS)
    ignore_pattern = re.compile(f"/({ignore_regex})$")

    filtered = [f for f in files if not ignore_pattern.search(f)]
    return filtered


def extract_connector_paths(files: list[str]) -> list[str]:
    """Extract connector paths from file list.

    >>> extract_connector_paths(["airbyte-integrations/connectors/source-faker/setup.py"])
    ['airbyte-integrations/connectors/source-faker/setup.py']
    >>> extract_connector_paths(["airbyte-integrations/connectors/destination-bigquery/build.gradle"])
    ['airbyte-integrations/connectors/destination-bigquery/build.gradle']
    >>> extract_connector_paths(["docs/some-file.md"])
    []
    >>> extract_connector_paths(["airbyte-integrations/connectors/source-faker/"])
    ['airbyte-integrations/connectors/source-faker/']
    """
    connector_pattern = re.compile(r"^airbyte-integrations/connectors/(source-[^/]+|destination-[^/]+)(/|$)")
    return [f for f in files if connector_pattern.match(f)]


def extract_connector_names(paths: list[str]) -> list[str]:
    """Extract unique connector directory names from paths."""
    connector_pattern = re.compile(r"airbyte-integrations/connectors/([^/]+)")
    connectors = set()

    for path in paths:
        match = connector_pattern.match(path)
        if match:
            connector_name = match.group(1)
            connector_dir = CONNECTORS_DIR / connector_name
            if connector_dir.exists():
                connectors.add(connector_name)
            else:
                print(
                    f"⚠️ '{connector_name}' directory was not found. " "This can happen if a connector is removed. Skipping.",
                    file=sys.stderr,
                )

    return sorted(connectors)


def get_connector_language(connector: str) -> str | None:
    """Read metadata.yaml and determine connector language."""
    metadata_path = CONNECTORS_DIR / connector / "metadata.yaml"

    if not metadata_path.exists():
        print(
            f"⚠️ metadata.yaml not found for '{connector}' " f"(looking at {metadata_path})",
            file=sys.stderr,
        )
        return None

    content = metadata_path.read_text()
    if re.search(r"language:java", content):
        return "java"
    elif re.search(r"language:python", content):
        return "python"
    else:
        return "unknown"


def find_local_cdk_connectors() -> list[str]:
    """Find Java connectors with useLocalCdk = true."""
    local_cdk_connectors = []

    print("Finding Java Bulk CDK connectors with version = local...", file=sys.stderr)

    for connector_dir in CONNECTORS_DIR.iterdir():
        if not connector_dir.is_dir():
            continue

        build_gradle = connector_dir / "build.gradle"
        build_gradle_kts = connector_dir / "build.gradle.kts"

        if build_gradle.exists():
            build_file = build_gradle
        elif build_gradle_kts.exists():
            build_file = build_gradle_kts
        else:
            continue

        content = build_file.read_text()

        if "airbyteBulkConnector" in content and re.search(r"cdk\s*=\s*['\"]local['\"]", content):
            local_cdk_connectors.append(connector_dir.name)

    return local_cdk_connectors


def return_empty_json() -> str:
    """Return empty JSON matrix format for GitHub Actions.

    >>> return_empty_json()
    '{"include": []}'
    """
    return '{"include": []}'


def format_output(connectors: list[str], json_output: bool) -> str:
    """Format connector list as JSON matrix or newline-delimited.

    >>> format_output(["source-faker", "destination-bigquery"], json_output=False)
    'source-faker\\ndestination-bigquery'
    >>> format_output(["source-faker"], json_output=True)
    '{"connector": ["source-faker"]}'
    >>> format_output([], json_output=True)
    '{"include": []}'
    >>> format_output([], json_output=False)
    ''
    """
    if not json_output:
        return "\n".join(connectors)

    if not connectors:
        return return_empty_json()

    return json.dumps({"connector": connectors})


def get_modified_connectors(
    java: bool = False,
    no_java: bool = False,
    json: bool = False,
    prev_commit: bool = False,
    local_cdk: bool = False,
    files_list: str | None = None,
) -> None:
    """
    List Airbyte connectors modified in the current branch.

    Called by poethepoet as: poe get-modified-connectors [flags]
    """
    files = get_modified_files(prev_commit, files_list)

    filtered = filter_ignored_files(files)
    if not filtered:
        print(
            "⚠️ Warning: No files remaining after filtering. Returning empty connector list.",
            file=sys.stderr,
        )
        if json:
            print(return_empty_json())
        return

    connector_paths = extract_connector_paths(filtered)
    if not connector_paths:
        print(
            "⚠️ Warning: No connector paths found. Returning empty connector list.",
            file=sys.stderr,
        )
        if json:
            print(return_empty_json())
        return

    connectors = extract_connector_names(connector_paths)
    if not connectors:
        print(
            "⚠️ Warning: Failed to extract connector directories. Returning empty connector list.",
            file=sys.stderr,
        )
        if json:
            print(return_empty_json())
        return

    if local_cdk:
        local_cdk_connectors = find_local_cdk_connectors()
        connectors = sorted(set(connectors) | set(local_cdk_connectors))

    if java or no_java:
        java_connectors = []
        for connector in connectors:
            lang = get_connector_language(connector)
            if lang == "java":
                java_connectors.append(connector)

        if java:
            connectors = java_connectors
        else:  # no_java
            connectors = [c for c in connectors if c not in java_connectors]

    print(format_output(connectors, json))


def generate_enhanced_matrix(
    repo: str,
    local_cdk: bool = False,
    files_list: str | None = None,
) -> None:
    """
    Generate enhanced GitHub Actions matrix with language detection and runner assignment.

    Called by poethepoet as: poe generate-connector-matrix <repo> [flags]
    """
    files = get_modified_files(prev_commit=False, files_list=files_list)
    filtered = filter_ignored_files(files)

    if not filtered:
        print(return_empty_json())
        return

    connector_paths = extract_connector_paths(filtered)
    if not connector_paths:
        print(return_empty_json())
        return

    connectors = extract_connector_names(connector_paths)
    if not connectors:
        print(return_empty_json())
        return

    if local_cdk:
        local_cdk_connectors = find_local_cdk_connectors()
        connectors = sorted(set(connectors) | set(local_cdk_connectors))

    matrix_items = []
    for connector in connectors:
        lang = get_connector_language(connector)

        if lang == "java":
            if repo.startswith("airbytehq/"):
                runner = "linux-24.04-large"
            else:
                runner = "ubuntu-latest"
        else:
            runner = "ubuntu-latest"

        matrix_items.append(
            {
                "connector": connector,
                "language": lang or "unknown",
                "runner": runner,
            }
        )

    if not matrix_items:
        print(return_empty_json())
    else:
        print(json.dumps({"include": matrix_items}))


if __name__ == "__main__":
    if "--run-tests" in sys.argv:
        print("Running doctests...", file=sys.stderr)
        result = doctest.testmod(verbose=True)
        if result.failed == 0:
            print(f"\n✅ All {result.attempted} doctests passed!", file=sys.stderr)
            sys.exit(0)
        else:
            print(f"\n❌ {result.failed} of {result.attempted} doctests failed!", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage:", file=sys.stderr)
        print("  ./poe-tasks/connector_matrix.py --run-tests", file=sys.stderr)
        print("\nThis script is designed to be called via poethepoet:", file=sys.stderr)
        print("  poe get-modified-connectors [flags]", file=sys.stderr)
        print("  poe generate-connector-matrix <repo> [flags]", file=sys.stderr)
        sys.exit(1)
