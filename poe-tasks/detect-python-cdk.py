#!/usr/bin/env -S uv run --script
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["tomli"]
# ///

"""
Detect and analyze airbyte-cdk dependency information from pyproject.toml files.

This script provides multiple modes for analyzing CDK dependencies:
- JSON output with complete dependency information
- Extras-only output for poetry add commands
- Version pin verification for production readiness

The script uses uv's automatic virtual environment management to handle dependencies.
For more information about uv script execution, see:
https://docs.astral.sh/uv/guides/scripts/#using-a-shebang-to-create-an-executable-file

For details about PEP 723 inline script metadata format, see:
https://peps.python.org/pep-0723/#how-to-teach-this

Usage:
    ./detect-python-cdk.py [directory]
        Return JSON string with complete CDK dependency information

    ./detect-python-cdk.py --extras-only [directory]
        Return string for use in: poetry add "airbyte-cdk$OUTPUT@version"
        Output examples: "" (no extras), "[sql]", "[sql,vector-db-based]"

    ./detect-python-cdk.py --detect-prerelease [directory]
        Exit 0 if CDK pinned to standard version, exit 1 if git/local/non-standard ref
        Provides guidance for resolving non-production references

Examples:
    ./detect-python-cdk.py /path/to/destination-motherduck
    {"version": "^6.0.0", "extras": ["sql"], "type": "standard", "is_production_ready": true}

    ./detect-python-cdk.py --extras-only /path/to/destination-motherduck
    [sql]

    ./detect-python-cdk.py --detect-prerelease /path/to/destination-motherduck
    ✅ Production ready: Standard version: ^6.0.0 with extras ['sql']
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import cast


try:
    import tomli
except ImportError:
    import tomllib as tomli


def parse_cdk_dependency(pyproject_path) -> dict:
    """Parse CDK dependency from pyproject.toml and return structured information.

    Base version strings will be normalized to {"version": "x.y.z"} format.

    Returns:
        dict: Complete dependency information including version, extras, type, etc.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
    except Exception as e:
        return {"error": f"Error reading pyproject.toml: {e}"}

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    cdk_dep = dependencies.get("airbyte-cdk")

    if not cdk_dep:
        return {"error": "No airbyte-cdk dependency found"}

    if isinstance(cdk_dep, str):
        # Normalize concise version syntax like `airbyte-cdk = "^6.0.0"`
        cdk_dep = {"version": cdk_dep}

    result = cast(dict[str, str | bool], cdk_dep.copy())
    result["dependency_type"] = "unknown"
    for dependency_type in ["version", "git", "path", "url"]:
        if dependency_type in result:
            result["dependency_type"] = dependency_type
            if dependency_type == "version":
                result["is_prerelease"] = is_prerelease_version(cdk_dep["version"])

            break

    return result


def is_prerelease_version(version_str) -> bool:
    """Check if version string represents a standard published version.

    Handles comma-separated version ranges like ">=6.61.6,<7.0" by validating
    each constraint separately. Returns True if any constraint is invalid or
    contains prerelease markers.
    """
    if not version_str:
        return True

    parts = [p.strip() for p in version_str.split(",") if p.strip()]

    constraint_pattern = re.compile(r"^(?:\^|~|~=|==|!=|<=|>=|<|>)?\s*\d+(?:\.\d+){0,2}\s*$")

    prerelease_pattern = re.compile(r"(?:a|alpha|b|beta|c|rc|pre|preview|dev)\d*$", re.IGNORECASE)

    for part in parts:
        if "*" in part or "x" in part.lower():
            return True

        if prerelease_pattern.search(part):
            return True

        if not constraint_pattern.match(part):
            return True

    return False


def format_extras_for_poetry(extras) -> str:
    """Format extras list for use in poetry add command.

    E.g. if extras is ['sql', 'vector-db-based'], return "[sql,vector-db-based]".
    """
    if not extras:
        return ""

    return f"[{','.join(extras)}]"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect and analyze airbyte-cdk dependency information", formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("directory", nargs="?", default=".", help="Directory containing pyproject.toml (default: current directory)")

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--extras-only", action="store_true", help="Return extras string for poetry add command")
    mode_group.add_argument("--detect-prerelease", action="store_true", help="Verify CDK is pinned to standard version (exit 1 if not)")

    args = parser.parse_args()

    connector_dir = Path(args.directory)
    pyproject_path = connector_dir / "pyproject.toml"

    if not pyproject_path.exists():
        if args.extras_only:
            return
        elif args.detect_prerelease:
            print(f"Error: pyproject.toml not found in {connector_dir}")
            sys.exit(1)
        else:
            print(json.dumps({"error": f"pyproject.toml not found in {connector_dir}"}))
            return

    cdk_info = parse_cdk_dependency(pyproject_path)

    if args.extras_only:
        extras = cdk_info.get("extras", [])
        print(format_extras_for_poetry(extras), flush=True)
    else:
        print(json.dumps(cdk_info), flush=True)

    if args.detect_prerelease:
        if cdk_info.get("is_prerelease") is not False:
            print(
                "❌ Pre-release CDK version detected.\n"
                "📝 Before merging your PR, remember to run `poe use-cdk-latest` to re-pin to the "
                "latest production CDK version.",
                flush=True,
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"✅ Production ready CDK version: {cdk_info.get('version')}", flush=True, file=sys.stderr)


if __name__ == "__main__":
    main()
