#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from pathlib import Path

import tomllib


def test_minimum_python_version_is_311_or_higher():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    dependencies = tomllib.loads(pyproject_path.read_text())["tool"]["poetry"]["dependencies"]
    version_clause = dependencies["python"].split(",")[0]
    match = re.match(r"^[\^~>=\s]*(\d+)\.(\d+)", version_clause)

    assert match is not None, f"Could not parse Python version clause: {version_clause!r}"
    version = (int(match.group(1)), int(match.group(2)))
    assert version >= (3, 11), f"Minimum supported Python version must be 3.11 or higher; found {version_clause!r}"
