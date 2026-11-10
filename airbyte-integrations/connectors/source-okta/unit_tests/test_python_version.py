#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from pathlib import Path

import tomllib


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]


def test_python_lower_bound_is_at_least_3_11():
    pyproject = tomllib.loads((CONNECTOR_ROOT / "pyproject.toml").read_text())
    constraint = pyproject["tool"]["poetry"]["dependencies"]["python"]
    match = re.match(r"^\^?\s*(\d+)\.(\d+)", constraint)

    assert match is not None, f"Could not parse Python version constraint: {constraint!r}"
    assert tuple(map(int, match.groups())) >= (3, 11), f"Python constraint {constraint!r} must be at least 3.11"


def test_lock_file_matches_python_constraint():
    pyproject = tomllib.loads((CONNECTOR_ROOT / "pyproject.toml").read_text())
    poetry_lock = tomllib.loads((CONNECTOR_ROOT / "poetry.lock").read_text())

    assert poetry_lock["metadata"]["python-versions"] == pyproject["tool"]["poetry"]["dependencies"]["python"]
