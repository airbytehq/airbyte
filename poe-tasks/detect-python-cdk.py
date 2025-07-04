#!/usr/bin/env -S uv run --script
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["tomli"]
# ///

"""
Detect and analyze airbyte-cdk dependency information from pyproject.toml files.

This consolidated script provides multiple modes for analyzing CDK dependencies:
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

    ./detect-python-cdk.py --verify-version-pin [directory]
        Exit 0 if CDK pinned to standard version, exit 1 if git/local/non-standard ref
        Provides guidance for resolving non-production references

Examples:
    ./detect-python-cdk.py /path/to/destination-motherduck
    {"version": "^6.0.0", "extras": ["sql"], "type": "standard", "production_ready": true}

    ./detect-python-cdk.py --extras-only /path/to/destination-motherduck
    [sql]

    ./detect-python-cdk.py --verify-version-pin /path/to/destination-motherduck
    ✅ Production ready: Standard version: ^6.0.0 with extras ['sql']
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    import tomllib as tomli


def parse_cdk_dependency(pyproject_path):
    """
    Parse CDK dependency from pyproject.toml and return structured information.
    
    Returns:
        dict: Complete dependency information including version, extras, type, etc.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
    except Exception as e:
        return {
            "error": f"Error reading pyproject.toml: {e}",
            "production_ready": False
        }

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    cdk_dep = dependencies.get("airbyte-cdk")

    if not cdk_dep:
        return {
            "error": "No airbyte-cdk dependency found",
            "production_ready": False
        }

    result = {
        "raw_dependency": cdk_dep,
        "extras": [],
        "version": None,
        "type": "unknown",
        "production_ready": False
    }

    if isinstance(cdk_dep, str):
        result["version"] = cdk_dep
        result["type"] = "string"
        result["production_ready"] = is_standard_version(cdk_dep)
        result["raw_dependency"] = {"version": cdk_dep}
        
    elif isinstance(cdk_dep, dict):
        if "git" in cdk_dep:
            result["type"] = "git"
            result["git_url"] = cdk_dep["git"]
            result["git_ref"] = cdk_dep.get("branch", cdk_dep.get("rev", "unknown"))
            result["production_ready"] = False
            
        elif "path" in cdk_dep:
            result["type"] = "local_path"
            result["local_path"] = cdk_dep["path"]
            result["production_ready"] = False
            
        elif "url" in cdk_dep:
            result["type"] = "url"
            result["url"] = cdk_dep["url"]
            result["production_ready"] = False
            
        else:
            result["type"] = "dict"
            version = cdk_dep.get("version")
            if version:
                result["version"] = version
                result["production_ready"] = is_standard_version(version)
        
        result["extras"] = cdk_dep.get("extras", [])
    
    return result


def is_standard_version(version_str):
    """Check if version string represents a standard published version."""
    if not version_str:
        return False

    version_pattern = r"^[~^>=<]*\d+\.\d+\.\d+([a-zA-Z0-9\-\.]*)?$"
    return bool(re.match(version_pattern, version_str.strip()))


def format_extras_for_poetry(extras):
    """Format extras list for use in poetry add command."""
    if not extras:
        return ""
    return f"[{','.join(extras)}]"


def verify_version_pin(cdk_info, connector_name):
    """Verify CDK version pin and provide guidance if not production ready."""
    if cdk_info.get("error"):
        print(f"❌ Error: {cdk_info['error']}")
        return False

    if cdk_info["production_ready"]:
        version = cdk_info.get("version", "unknown")
        extras = cdk_info.get("extras", [])
        extras_str = f" with extras {extras}" if extras else ""
        print(f"✅ Production ready: Standard version: {version}{extras_str}")
        return True
    else:
        print("❌ This connector is not ready for production release.")
        
        if cdk_info["type"] == "git":
            git_url = cdk_info.get("git_url", "unknown")
            git_ref = cdk_info.get("git_ref", "unknown")
            print(f"   Issue: Git reference: {git_url}#{git_ref}")
        elif cdk_info["type"] == "local_path":
            local_path = cdk_info.get("local_path", "unknown")
            print(f"   Issue: Local path reference: {local_path}")
        elif cdk_info["type"] == "url":
            url = cdk_info.get("url", "unknown")
            print(f"   Issue: URL reference: {url}")
        elif cdk_info["type"] == "string":
            print(f"   Issue: Non-standard version string: {cdk_info.get('version', 'unknown')}")
        else:
            print(f"   Issue: Unexpected dependency format: {cdk_info.get('raw_dependency', 'unknown')}")
        
        print()
        print("   It is currently pinning its CDK version to a local or git-based ref.")
        print("   To resolve, use `poe use-cdk-latest` after your working dev version")
        print("   of the CDK has been published.")
        if connector_name:
            print(f"   You can also use the slash command in your PR: `/poe connector {connector_name} use-cdk-latest`")
        
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Detect and analyze airbyte-cdk dependency information",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing pyproject.toml (default: current directory)"
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--extras-only",
        action="store_true",
        help="Return extras string for poetry add command"
    )
    mode_group.add_argument(
        "--verify-version-pin",
        action="store_true",
        help="Verify CDK is pinned to standard version (exit 1 if not)"
    )
    
    args = parser.parse_args()
    
    connector_dir = Path(args.directory)
    pyproject_path = connector_dir / "pyproject.toml"

    if not pyproject_path.exists():
        if args.extras_only:
            return
        elif args.verify_version_pin:
            print(f"Error: pyproject.toml not found in {connector_dir}")
            sys.exit(1)
        else:
            print(json.dumps({"error": f"pyproject.toml not found in {connector_dir}"}))
            return

    cdk_info = parse_cdk_dependency(pyproject_path)
    
    if args.extras_only:
        extras = cdk_info.get("extras", [])
        print(format_extras_for_poetry(extras))
        
    elif args.verify_version_pin:
        resolved_dir = connector_dir.resolve()
        connector_name = None
        
        if resolved_dir.name.startswith(("source-", "destination-")):
            connector_name = resolved_dir.name
        elif not resolved_dir.name.startswith(("source-", "destination-")):
            print(f"Warning: Directory '{resolved_dir.name}' doesn't start with 'source-' or 'destination-'")
        
        success = verify_version_pin(cdk_info, connector_name)
        sys.exit(0 if success else 1)
        
    else:
        print(json.dumps(cdk_info, indent=2))


if __name__ == "__main__":
    main()
