#!/usr/bin/env -S uv run --script
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
# dependencies = ["tomli"]

"""
Check if connector is using non-production CDK references.

This script checks if the airbyte-cdk dependency in pyproject.toml is pinned to
a git reference, local reference, or other non-standard version that would prevent
production release.

The script uses uv's automatic virtual environment management to handle dependencies.
For more information about uv script execution, see:
https://docs.astral.sh/uv/guides/scripts/#using-a-shebang-to-create-an-executable-file

For details about PEP 723 inline script metadata format, see:
https://peps.python.org/pep-0723/#how-to-teach-this

Usage:
    ./poetry-check-non-prod-cdk.py
    ./poetry-check-non-prod-cdk.py /path/to/connector

Returns:
    0: CDK is pinned to a standard version (production ready)
    1: CDK is pinned to git/local/non-standard ref (not production ready)

Examples:
    airbyte-cdk = "^6.0.0"
    airbyte-cdk = {version = "6.0.0", extras = ["sql"]}

    airbyte-cdk = {git = "https://github.com/...", branch = "main"}
    airbyte-cdk = {path = "../local-cdk"}

    ./poetry-check-non-prod-cdk.py
    ✅ Production ready: Standard version: ^6.0.0 with extras ['sql']

    ./poetry-check-non-prod-cdk.py /path/to/dev-connector
    ❌ This connector is not ready for production release.
       Issue: Git reference: https://github.com/airbytehq/airbyte-python-cdk.git#main
"""

import re
import sys
from pathlib import Path

try:
    import tomllib as tomli
except ImportError:
    import tomli


def is_standard_version(version_str):
    """Check if version string represents a standard published version."""
    if not version_str:
        return False

    version_pattern = r"^[~^>=<]*\d+\.\d+\.\d+([a-zA-Z0-9\-\.]*)?$"
    return bool(re.match(version_pattern, version_str.strip()))


def check_cdk_dependency(pyproject_path):
    """
    Check CDK dependency and return (is_production_ready, dependency_info).

    Returns:
        tuple: (bool, str) - (is_production_ready, dependency_description)
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
    except Exception as e:
        return False, f"Error reading pyproject.toml: {e}"

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    cdk_dep = dependencies.get("airbyte-cdk")

    if not cdk_dep:
        return False, "No airbyte-cdk dependency found"

    if isinstance(cdk_dep, str):
        if is_standard_version(cdk_dep):
            return True, f"Standard version: {cdk_dep}"
        else:
            return False, f"Non-standard version string: {cdk_dep}"

    elif isinstance(cdk_dep, dict):
        if "git" in cdk_dep:
            git_url = cdk_dep["git"]
            branch = cdk_dep.get("branch", cdk_dep.get("rev", "unknown"))
            return False, f"Git reference: {git_url}#{branch}"

        if "path" in cdk_dep:
            path = cdk_dep["path"]
            return False, f"Local path reference: {path}"

        if "url" in cdk_dep:
            url = cdk_dep["url"]
            return False, f"URL reference: {url}"

        version = cdk_dep.get("version")
        if version and is_standard_version(version):
            extras = cdk_dep.get("extras", [])
            extras_str = f" with extras {extras}" if extras else ""
            return True, f"Standard version: {version}{extras_str}"
        elif version:
            return False, f"Non-standard version in dict: {version}"
        else:
            return False, f"Dict format without version: {cdk_dep}"

    else:
        return False, f"Unexpected dependency format: {type(cdk_dep)}"


def main():
    connector_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    pyproject_path = connector_dir / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"Error: pyproject.toml not found in {connector_dir}")
        sys.exit(1)

    resolved_dir = connector_dir.resolve()
    if not resolved_dir.name.startswith(("source-", "destination-")):
        print(f"Error: Directory '{resolved_dir.name}' must start with 'source-' or 'destination-'")
        sys.exit(1)

    connector_name = resolved_dir.name

    is_production_ready, dependency_info = check_cdk_dependency(pyproject_path)

    if is_production_ready:
        print(f"✅ Production ready: {dependency_info}")
        sys.exit(0)
    else:
        print("❌ This connector is not ready for production release.")
        print(f"   Issue: {dependency_info}")
        print()
        print("   It is currently pinning its CDK version to a local or git-based ref.")
        print("   To resolve, use `poe use-cdk-latest` after your working dev version")
        print("   of the CDK has been published.")
        print(f"   You can also use the slash command in your PR: `/poe connector {connector_name} use-cdk-latest`")
        sys.exit(1)


if __name__ == "__main__":
    main()
