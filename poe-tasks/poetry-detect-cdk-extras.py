#!/usr/bin/env -S uv run --script
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
# dependencies = ["tomli"]

"""
Detect currently installed CDK extras from pyproject.toml file.

This script parses the pyproject.toml file in the specified directory (or current
directory if not provided) and extracts any extras specified for the airbyte-cdk dependency.

The script uses uv's automatic virtual environment management to handle dependencies.
For more information about uv script execution, see:
https://docs.astral.sh/uv/guides/scripts/#using-a-shebang-to-create-an-executable-file

For details about PEP 723 inline script metadata format, see:
https://peps.python.org/pep-0723/#how-to-teach-this

Usage:
    ./poetry-detect-cdk-extras.py

    ./poetry-detect-cdk-extras.py /path/to/connector

Examples:
    ./poetry-detect-cdk-extras.py /path/to/destination-motherduck
    [sql]

    ./poetry-detect-cdk-extras.py /path/to/source-file
    (no output)

    poe -qq get-cdk-extras
"""

import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    import tomllib as tomli


def main():
    connector_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    pyproject_path = connector_dir / "pyproject.toml"

    if not pyproject_path.exists():
        return

    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    cdk_dep = dependencies.get("airbyte-cdk")

    if isinstance(cdk_dep, dict):
        extras = cdk_dep.get("extras", [])
        print(f"[{','.join(extras)}]" if extras else "")


if __name__ == "__main__":
    main()
