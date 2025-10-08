#!/usr/bin/env -S uv run --python 3.12 --script
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

# /// script
# requires-python = "==3.12"
# dependencies = [
#   "pyyaml",
# ]
# ///
"""Generate GitHub Actions matrix for modified Airbyte connectors.

This script replaces get-modified-connectors.sh with a more maintainable Python implementation.
It detects modified connector directories and outputs them in text or JSON format for CI workflows.

Usage:
    poe get-modified-connectors

    poe get-modified-connectors --json

    poe get-modified-connectors --java --json

    poe get-modified-connectors --no-java --json

    poe get-modified-connectors --certified --json

    poe get-modified-connectors --no-certified --json

    poe get-modified-connectors --local-cdk --json

    poe get-modified-connectors --files-list "airbyte-integrations/connectors/source-faker/metadata.yaml,airbyte-integrations/connectors/destination-bigquery/README.md"

Testing:
    ./poe-tasks/get_connector_matrix.py --run-tests

    python -m doctest poe-tasks/get_connector_matrix.py -v

Contributing:
    When adding new functions to this script, please include doctests that demonstrate
    the expected behavior. Doctests serve as both documentation and unit tests.

    For more information on doctests, see:
    https://docs.python.org/3/library/doctest.html
"""

import json
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional


def get_modified_files(files_list: Optional[str] = None, prev_commit: bool = False) -> list[str]:
    """Get list of modified files from git or override string.

    Args:
        files_list: Optional CSV string of file paths to override git detection
        prev_commit: If True, compare with previous commit instead of master

    Returns:
        List of modified file paths

    >>> files = get_modified_files(files_list="file1.py,file2.md,file3.yaml")
    >>> files
    ['file1.py', 'file2.md', 'file3.yaml']
    >>> get_modified_files(files_list="")
    []
    >>> isinstance(get_modified_files(files_list=None), list)
    True
    """
    if files_list is not None:
        if not files_list.strip():
            return []
        return [f.strip() for f in files_list.split(",") if f.strip()]

    try:
        subprocess.run(["git", "remote", "get-url", "upstream"], check=True, capture_output=True, text=True)
        remote = "upstream"
    except subprocess.CalledProcessError:
        remote = "origin"

    default_branch = "master"

    subprocess.run(["git", "fetch", "--quiet", remote, default_branch], check=True)

    all_files = []

    if prev_commit:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD"], capture_output=True, text=True, check=True
        )
        all_files = result.stdout.strip().split("\n") if result.stdout.strip() else []
    else:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{remote}/{default_branch}...HEAD"], capture_output=True, text=True, check=True
        )
        committed = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=True)
        staged = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
        unstaged = result.stdout.strip().split("\n") if result.stdout.strip() else []

        result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, check=True)
        untracked = result.stdout.strip().split("\n") if result.stdout.strip() else []

        all_files = committed + staged + unstaged + untracked

    return list(set(f for f in all_files if f))


def filter_ignored_files(files: list[str]) -> list[str]:
    """Filter out files that should be ignored.

    >>> filter_ignored_files(
    ...     ["airbyte-integrations/connectors/source-faker/metadata.yaml", "airbyte-integrations/connectors/source-faker/README.md"]
    ... )
    ['airbyte-integrations/connectors/source-faker/metadata.yaml']
    >>> filter_ignored_files(["poe-tasks/poe_tasks.toml", "airbyte-integrations/connectors/source-faker/.coveragerc"])
    []
    >>> filter_ignored_files(["airbyte-integrations/connectors/source-faker/src/main.py"])
    ['airbyte-integrations/connectors/source-faker/src/main.py']
    """
    ignore_patterns = [
        r"/\.coveragerc$",
        r"/poe_tasks\.toml$",
        r"/README\.md$",
    ]

    filtered = []
    for file in files:
        should_ignore = False
        for pattern in ignore_patterns:
            if re.search(pattern, file):
                should_ignore = True
                break
        if not should_ignore:
            filtered.append(file)

    return filtered


def extract_connector_paths(files: list[str]) -> list[str]:
    """Extract connector directory paths from file paths.

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


def extract_connector_names(connector_paths: list[str]) -> list[str]:
    """Extract connector names from connector paths.

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
    """
    import yaml

    metadata_path = Path(f"airbyte-integrations/connectors/{connector_name}/metadata.yaml")

    if not metadata_path.exists():
        print(f"⚠️ metadata.yaml not found for '{connector_name}' (looking at {metadata_path})", file=sys.stderr)
        return {}

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
        return local_cdk_connectors

    for connector_dir in connectors_dir.iterdir():
        if not connector_dir.is_dir():
            continue

        build_file = None
        if (connector_dir / "build.gradle").exists():
            build_file = connector_dir / "build.gradle"
        elif (connector_dir / "build.gradle.kts").exists():
            build_file = connector_dir / "build.gradle.kts"

        if build_file:
            content = build_file.read_text()
            if "airbyteBulkConnector" in content and re.search(r"cdk\s*=\s*['\"]local['\"]", content):
                local_cdk_connectors.append(connector_dir.name)

    return sorted(local_cdk_connectors)


def is_java_connector(connector_name: str) -> bool:
    """Check if a connector is Java-based by reading its metadata.yaml.

    Args:
        connector_name: Name of the connector (e.g., 'source-faker')

    Returns:
        True if the connector uses Java, False otherwise
    """
    manifest = get_manifest_dict(connector_name)
    if not manifest:
        return False

    language = manifest.get("data", {}).get("language", "")
    return language == "java"


def is_certified_connector(connector_name: str) -> bool:
    """Check if a connector is certified by reading its metadata.yaml.

    Args:
        connector_name: Name of the connector (e.g., 'source-faker')

    Returns:
        True if the connector has supportLevel: certified, False otherwise
    """
    manifest = get_manifest_dict(connector_name)
    if not manifest:
        return False

    support_level = manifest.get("data", {}).get("supportLevel", "")
    return support_level == "certified"


def filter_by_language(connectors: list[str], java_only: bool = False, no_java: bool = False) -> list[str]:
    """Filter connectors by language (Java or non-Java).

    Args:
        connectors: List of connector names
        java_only: If True, return only Java connectors
        no_java: If True, return only non-Java connectors

    Returns:
        Filtered list of connector names
    """
    if not java_only and not no_java:
        return connectors

    java_connectors = [c for c in connectors if is_java_connector(c)]

    if java_only:
        return java_connectors

    if no_java:
        return [c for c in connectors if c not in java_connectors]

    return connectors


def filter_by_support_level(connectors: list[str], certified_only: bool = False, no_certified: bool = False) -> list[str]:
    """Filter connectors by support level (certified or non-certified).

    Args:
        connectors: List of connector names
        certified_only: If True, return only certified connectors
        no_certified: If True, return only non-certified connectors

    Returns:
        Filtered list of connector names
    """
    if not certified_only and not no_certified:
        return connectors

    certified_connectors = [c for c in connectors if is_certified_connector(c)]

    if certified_only:
        return certified_connectors

    if no_certified:
        return [c for c in connectors if c not in certified_connectors]

    return connectors


def return_empty_json() -> str:
    """Return empty JSON matrix format for GitHub Actions.

    >>> return_empty_json()
    '{"connector": [""]}'
    """
    return '{"connector": [""]}'


def format_output(connectors: list[str], json_output: bool = False) -> str:
    """Format connector list as text or JSON.

    Args:
        connectors: List of connector names
        json_output: If True, output in GitHub Actions matrix JSON format

    Returns:
        Formatted output string

    >>> format_output(["source-faker", "destination-bigquery"], json_output=False)
    'source-faker\\ndestination-bigquery'
    >>> format_output(["source-faker"], json_output=True)
    '{"connector": ["source-faker"]}'
    >>> format_output([], json_output=True)
    '{"connector": [""]}'
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
    certified: bool = False,
    no_certified: bool = False,
    json: bool = False,
    prev_commit: bool = False,
    local_cdk: bool = False,
    files_list: Optional[str] = None,
) -> None:
    """Main function to get modified connectors and output them.

    This function is called by poethepoet and handles all the logic.
    """
    modified_files = get_modified_files(files_list=files_list, prev_commit=prev_commit)

    filtered = filter_ignored_files(modified_files)
    if not filtered and not local_cdk:
        print("⚠️ Warning: No files remaining after filtering. Returning empty connector list.", file=sys.stderr)
        if json:
            print(return_empty_json())
        return

    connector_paths = extract_connector_paths(filtered)
    if not connector_paths and not local_cdk:
        print("⚠️ Warning: No connector paths found. Returning empty connector list.", file=sys.stderr)
        if json:
            print(return_empty_json())
        return

    connectors = extract_connector_names(connector_paths)

    if local_cdk:
        print("Finding Java Bulk CDK connectors with version = local...", file=sys.stderr)
        local_cdk_connectors = find_local_cdk_connectors()
        connectors = sorted(list(set(connectors + local_cdk_connectors)))

    if not connectors:
        print("⚠️ Warning: No connectors found. Returning empty connector list.", file=sys.stderr)
        if json:
            print(return_empty_json())
        return

    connectors = filter_by_language(connectors, java_only=java, no_java=no_java)
    connectors = filter_by_support_level(connectors, certified_only=certified, no_certified=no_certified)

    output = format_output(connectors, json_output=json)
    if output:
        print(output)


def run_doctests() -> None:
    """Run all doctests in this module and report results."""
    import doctest

    print("🧪 Running doctests...")
    results = doctest.testmod(verbose=False)

    if results.failed == 0:
        print(f"✅ All {results.attempted} doctests passed!")
        sys.exit(0)
    else:
        print(f"❌ {results.failed} of {results.attempted} doctests failed!")
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate GitHub Actions matrix for modified Airbyte connectors")
    parser.add_argument("--java", action="store_true", help="Filter to only Java connectors")
    parser.add_argument("--no-java", action="store_true", help="Filter to exclude Java connectors")
    parser.add_argument("--certified", action="store_true", help="Filter to only certified connectors")
    parser.add_argument("--no-certified", action="store_true", help="Filter to exclude certified connectors")
    parser.add_argument("--json", action="store_true", help="Output in GitHub Actions matrix JSON format")
    parser.add_argument("--prev-commit", action="store_true", help="Compare with previous commit instead of master")
    parser.add_argument("--local-cdk", action="store_true", help="Include connectors using local CDK")
    parser.add_argument("--files-list", help="CSV string of file paths (overrides git detection)")
    parser.add_argument("--run-tests", action="store_true", help="Run doctests and exit")

    args = parser.parse_args()

    if args.run_tests:
        run_doctests()
        return

    get_modified_connectors(
        java=args.java,
        no_java=args.no_java,
        certified=args.certified,
        no_certified=args.no_certified,
        json=args.json,
        prev_commit=args.prev_commit,
        local_cdk=args.local_cdk,
        files_list=args.files_list,
    )


if __name__ == "__main__":
    main()
