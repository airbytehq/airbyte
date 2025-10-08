#!/usr/bin/env -S uv run --python 3.12 --script --no-project
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

# /// script
# requires-python = "==3.12"
# dependencies = [
#   "pyyaml",
#   "typer",
#   "pytest",
# ]
# ///
"""Generate GitHub Actions matrix for modified Airbyte connectors.

This script replaces get-modified-connectors.sh with a more maintainable Python implementation.
It detects modified connector directories and outputs them in text or JSON format for CI workflows.

Usage:
    # Show usage syntax:
    poe get-modified-connectors --help

    # Get modified connectors compared to master:
    poe get-modified-connectors
    poe get-modified-connectors --json
    poe get-modified-connectors --java --json
    poe get-modified-connectors --no-java --json
    poe get-modified-connectors --certified --json
    poe get-modified-connectors --no-certified --json
    poe get-modified-connectors --local-cdk --json

    # Get modified connectors with overridden files list:
    poe get-modified-connectors --files-list "airbyte-integrations/connectors/source-faker/metadata.yaml,airbyte-integrations/connectors/destination-bigquery/README.md"

    # Run all tests:
    poe get-modified-connectors --run-tests

Contributing:
    When adding new functions to this script, please include doctests that demonstrate
    the expected behavior. Doctest tests serve as both documentation and unit tests.

    Confirm your changes work by running:
        poe get-modified-connectors --run-tests
    Or:
        uv run poe-tasks/get_connector_matrix.py --run-tests

    For more information on doctest, see: https://docs.python.org/3/library/doctest.html
"""

import json
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated


def get_modified_files(
    prev_commit: bool = False,
) -> list[str]:
    """Get list of modified files from git or override string.

    Args:
        prev_commit: If True, compare with previous commit instead of master

    Returns:
        List of modified file paths

    Doctest Examples:

    >>> isinstance(get_modified_files(prev_commit=True), list)
    True
    >>> isinstance(get_modified_files(prev_commit=False), list)
    True
    """
    try:
        subprocess.run(
            ["git", "remote", "get-url", "upstream"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        remote = "origin"
    else:
        # No exception raised
        remote = "upstream"

    default_branch = "master"

    subprocess.run(
        ["git", "fetch", "--quiet", remote, default_branch],
        check=True,
    )

    all_files: list[str] = []
    result: subprocess.CompletedProcess[str]

    if prev_commit:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"], capture_output=True, text=True, check=True
        )
        all_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
    else:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{remote}/{default_branch}...HEAD"], capture_output=True, text=True, check=True
        )
        committed: list[str] = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        staged: list[str] = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        unstaged: list[str] = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        )
        untracked: list[str] = result.stdout.strip().split("\n") if result.stdout.strip() else []
        all_files = committed + staged + unstaged + untracked

    return list(set(f for f in all_files if f))


def filter_ignored_files(
    files: list[str],
) -> list[str]:
    """Filter out files that should be ignored.

    Doctest Examples:

    >>> filter_ignored_files(
    ...     ["airbyte-integrations/connectors/source-faker/metadata.yaml", "airbyte-integrations/connectors/source-faker/README.md"]
    ... )
    ['airbyte-integrations/connectors/source-faker/metadata.yaml']
    >>> filter_ignored_files(["poe-tasks/poe_tasks.toml", "airbyte-integrations/connectors/source-faker/.coveragerc"])
    []
    >>> filter_ignored_files(["airbyte-integrations/connectors/source-faker/src/main.py"])
    ['airbyte-integrations/connectors/source-faker/src/main.py']
    """
    ignore_patterns: list[str] = [
        r"/\.coveragerc$",
        r"/poe_tasks\.toml$",
        r"/README\.md$",
    ]

    filtered: list[str] = []
    for file in files:
        should_ignore = False
        for pattern in ignore_patterns:
            if re.search(pattern, file):
                should_ignore = True
                break
        if not should_ignore:
            filtered.append(file)

    return filtered


def extract_connector_paths(
    files: list[str],
) -> list[str]:
    """Extract connector directory paths from file paths.

    Doctest Examples:

    >>> extract_connector_paths(["airbyte-integrations/connectors/source-faker/metadata.yaml"])
    ['airbyte-integrations/connectors/source-faker']
    >>> extract_connector_paths(["airbyte-integrations/connectors/destination-bigquery/build.gradle"])
    ['airbyte-integrations/connectors/destination-bigquery']
    >>> extract_connector_paths(["docs/integrations/sources/faker.md"])
    []
    >>> extract_connector_paths(
    ...     ["airbyte-integrations/connectors/source-faker/src/main.py", "airbyte-integrations/connectors/source-faker/metadata.yaml"]
    ... )
    ['airbyte-integrations/connectors/source-faker']
    """
    connector_pattern = r"^airbyte-integrations/connectors/((?:source-|destination-)[^/]+)(?:/|$)"
    connector_paths = set()

    for file in files:
        match = re.match(connector_pattern, file)
        if match:
            connector_dir = f"airbyte-integrations/connectors/{match.group(1)}"
            connector_paths.add(connector_dir)

    return sorted(list(connector_paths))


def extract_connector_names(
    connector_paths: list[str],
) -> list[str]:
    """Extract connector names from connector paths.

    Doctest Examples:

    >>> extract_connector_names(["airbyte-integrations/connectors/source-faker"])
    ['source-faker']
    >>> extract_connector_names(["airbyte-integrations/connectors/destination-bigquery", "airbyte-integrations/connectors/source-faker"])
    ['destination-bigquery', 'source-faker']
    >>> extract_connector_names([])
    []
    """
    connectors = []
    for path in connector_paths:
        if Path(path).is_dir():
            connector_name = Path(path).name
            connectors.append(connector_name)
        else:
            print(f"⚠️ '{path}' directory was not found. This can happen if a connector is removed. Skipping.", file=sys.stderr)

    return sorted(connectors)


@lru_cache(maxsize=None)
def get_manifest_dict(connector_name: str) -> dict:
    """Load and parse metadata.yaml for a connector (cached).

    Args:
        connector_name: Name of the connector (e.g., 'source-faker')

    Returns:
        Dictionary containing the parsed YAML content, or empty dict if not found

    Doctest Examples:
    >>> isinstance(get_manifest_dict("source-faker"), dict)
    True

    >>> from unittest.mock import patch, mock_open
    >>> with patch("builtins.open", mock_open(read_data='data:\\n  tags: ["language:java"]\\n')):
    ...     with patch("pathlib.Path.exists", return_value=True):
    ...         result = get_manifest_dict("test-connector")
    ...         result["data"]["tags"]
    ['language:java']
    """
    import yaml

    metadata_path = Path(f"airbyte-integrations/connectors/{connector_name}/metadata.yaml")

    if not metadata_path.exists():
        raise FileNotFoundError(f"File `metadata.yaml` not found for connector '{connector_name}' " f"at path: {metadata_path}")

    try:
        with open(metadata_path) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️ Failed to parse metadata.yaml for '{connector_name}': {e}", file=sys.stderr)
        return {}


def find_local_cdk_connectors() -> list[str]:
    """Find Java Bulk CDK connectors with cdk = 'local' in their build files.

    Returns:
        List of connector names using local CDK
    """
    local_cdk_connectors = []
    connectors_dir = Path("airbyte-integrations/connectors")

    if not connectors_dir.exists():
        raise FileNotFoundError(f"Connectors directory not found: {connectors_dir}")

    for connector_dir in connectors_dir.iterdir():
        if not connector_dir.is_dir():
            continue

        build_file: Path | None = next(
            (file for file in [connector_dir / "build.gradle", connector_dir / "build.gradle.kts"] if file.exists()),
            None,
        )
        if build_file:
            content = build_file.read_text()
            if "airbyteBulkConnector" in content and re.search(r"cdk\s*=\s*['\"]local['\"]", content):
                local_cdk_connectors.append(connector_dir.name)

    return sorted(local_cdk_connectors)


def is_java_connector(connector_name: str) -> bool:
    """Check if a connector is Java-based by reading its metadata.yaml.

    Args:
        connector_name: Name of the connector (e.g., 'source-faker')

    Contributor's Note:
        This function currently only checks for Java vs non-Java. It could
        be rewritten to simply return the language string if we need
        to support more languages in the future. (Java is the only language that
        has special CI handling as of now.)

    Returns:
        True if the connector uses Java, False otherwise

    Doctest Examples:
    >>> is_java_connector("source-faker")
    False
    >>> is_java_connector("destination-bigquery")
    True
    """
    manifest = get_manifest_dict(connector_name)
    if not manifest:
        return False

    if "language" in manifest.get("data", {}):
        language = manifest["data"]["language"]
        return language.lower() == "java"

    language_tag = manifest.get("data", {}).get("tags", [])
    return "language:java" in (tag.lower() for tag in language_tag)


def is_certified_connector(connector_name: str) -> bool:
    """Check if a connector is certified by reading its metadata.yaml.

    Args:
        connector_name: Name of the connector (e.g., 'source-faker')

    Returns:
        True if the connector has supportLevel: certified, False otherwise

    Doctest Examples:
    >>> is_certified_connector("source-faker")
    False
    >>> is_certified_connector("destination-bigquery")
    True
    """
    manifest = get_manifest_dict(connector_name)
    if not manifest:
        return False

    support_level = manifest.get("data", {}).get("supportLevel", "")
    return support_level == "certified"


def filter_by_language(
    connectors: list[str],
    java: Annotated[
        bool | None,
        "Filter to Java-only if True, non-Java if False.",
    ] = None,
) -> list[str]:
    """Filter connectors by language (Java or non-Java).

    Returns:
        Filtered list of connector names

    Contributor's Note:
        If use cases arise, this function can be extended to support other languages.
        Right now, we only actually need special handling for Java vs non-Java.

    Doctest Examples:
    >>> filter_by_language(["source-faker", "destination-bigquery"], java=True)
    ['destination-bigquery']
    >>> filter_by_language(["source-faker", "destination-bigquery"], java=False)
    ['source-faker']
    >>> filter_by_language(["source-faker", "destination-bigquery"], java=None)
    ['source-faker', 'destination-bigquery']
    """
    if java is None:
        return connectors

    return [c for c in connectors if is_java_connector(c) == java]


def filter_by_support_level(
    connectors: list[str],
    certified: bool | None = None,
) -> list[str]:
    """Filter connectors by support level (certified or non-certified).

    Args:
        connectors: List of connector names
        certified:
        - If True, return only certified connectors.
        - If False, return only non-certified connectors.
        - If None, return all connectors.

    Returns:
        Filtered list of connector names

    Doctest Examples:
    >>> filter_by_support_level(["source-faker", "destination-bigquery"], certified=True)
    ['destination-bigquery']
    >>> filter_by_support_level(["source-faker", "destination-bigquery"], certified=False)
    ['source-faker']
    >>> filter_by_support_level(["source-faker", "destination-bigquery"], certified=None)
    ['source-faker', 'destination-bigquery']
    """
    if certified is None:
        return connectors

    return [c for c in connectors if is_certified_connector(c) == certified]


def return_empty_json() -> str:
    """Return empty JSON matrix format for GitHub Actions.

    Doctest Examples:
    >>> return_empty_json()
    '{"connector": [""]}'
    """
    return '{"connector": [""]}'


def format_output(
    connectors: list[str],
    json_output: bool = False,
) -> str:
    """Format connector list as text or JSON.

    Args:
        connectors: List of connector names
        json_output: If True, output in GitHub Actions matrix JSON format

    Returns:
        Formatted output string

    Doctest Examples:
    >>> format_output(["source-faker", "destination-bigquery"], json_output=False)
    'source-faker\\ndestination-bigquery'
    >>> format_output(["source-faker"], json_output=True)
    '{"connector": ["source-faker"]}'
    >>> format_output([], json_output=True)
    '{"connector": [""]}'
    >>> format_output([], json_output=False)
    ''
    >>> format_output(["source-faker"], json_output=False)
    'source-faker'
    """
    if not json_output:
        return "\n".join(connectors)

    if not connectors:
        return return_empty_json()

    return json.dumps({"connector": connectors})


def get_modified_connectors(
    *,
    # This modifies the starting files list:
    prev_commit: bool = False,
    override_files_list: Optional[list[str]] = None,
) -> list[str]:
    """Function to get modified connectors and output them.

    This function gets modified files and filters them to find the relevant connectors.
    """
    modified_files: list[str]
    if override_files_list is not None:
        modified_files = override_files_list
        print(
            f"ℹ️ Using overridden files list with {len(modified_files)} entries.",
            file=sys.stderr,
        )
    else:
        modified_files = get_modified_files(prev_commit=prev_commit)

    if not modified_files:
        print(
            "⚠️ Warning: No modified files found. Returning empty connector list.",
            file=sys.stderr,
        )
        return []

    modified_files = filter_ignored_files(modified_files)
    if not modified_files:
        print(
            "⚠️ Warning: No files remaining after filtering. Returning empty connector list.",
            file=sys.stderr,
        )
        return []

    connector_paths = extract_connector_paths(modified_files)
    if not connector_paths:
        print(
            "⚠️ Warning: No connector paths found. Returning empty connector list.",
            file=sys.stderr,
        )
        return []

    connectors: list[str] = extract_connector_names(connector_paths)

    if not connectors:
        print(
            "⚠️ Warning: No connectors found. Returning empty connector list.",
            file=sys.stderr,
        )
        return []

    return connectors


app = typer.Typer(add_completion=False)


@app.command()
def main(
    files_list: Annotated[
        Optional[str],
        typer.Option(help="CSV string of file paths (overrides git detection).")
    ] = None,
    local_cdk: Annotated[
        bool,
        typer.Option(
            "--local-cdk",  # Don't auto-add the '--no-' inverse flag
            help="Get list of connectors using the local CDK (overrides git detection).",
        ),
    ] = False,
    prev_commit: Annotated[
        bool,
        typer.Option(
            "--prev-commit",  # Don't auto-add the '--no-' inverse flag
            help="Compare with previous commit instead of master.",
        ),
    ] = False,
    java: Annotated[
        bool | None,
        typer.Option(help="Filter to only Java connectors."),
    ] = None,
    certified: Annotated[
        bool | None,
        typer.Option(help="Filter to only certified connectors."),
    ] = None,
    json_matrix: Annotated[
        bool,
        typer.Option(help="Output in GitHub Actions matrix JSON format."),
    ] = False,
    run_tests: Annotated[
        bool,
        typer.Option(
            "--run-tests",  # Don't auto-add the '--no-' inverse flag
            help="Run doctest tests and exit (Ignores other options).",
        ),
    ] = False,
) -> None:
    """Generate GitHub Actions matrix for modified Airbyte connectors.

    Doctest Examples:

    >>> main(files_list="airbyte-integrations/connectors/source-faker/metadata.yaml", json_matrix=False)
    source-faker
    >>> main(
    ...     files_list="airbyte-integrations/connectors/source-faker/metadata.yaml,airbyte-integrations/connectors/destination-bigquery/README.md",
    ...     json_matrix=True,
    ... )
    {"connector": ["source-faker"]}
    """
    if run_tests:
        run_doctest_tests()
        return

    connectors_list: list[str]
    if local_cdk:
        connectors_list = find_local_cdk_connectors()

    else:
        connectors_list = get_modified_connectors(
            prev_commit=prev_commit,
            override_files_list=(None if files_list is None else [file.strip() for file in files_list.replace("\n", ",").split(",")]),
        )

    if java is not None:
        connectors_list = filter_by_language(connectors_list, java=java)

    if certified is not None:
        connectors_list = filter_by_support_level(connectors_list, certified=certified)

    output = format_output(connectors_list, json_output=json_matrix)
    if output:
        print(output)


def run_doctest_tests() -> None:
    """Run all doctest tests in this module and report results."""
    import pytest  # Defer import in case not running with uv

    args = [
        "-q",
        "--color=yes",
        "--doctest-modules",
        __file__,
    ]
    raise SystemExit(pytest.main(args))


if __name__ == "__main__":
    app()
