#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from pathlib import Path

import tomllib


CONNECTOR_ROOT = Path(__file__).resolve().parent.parent


def _python_constraint() -> str:
    pyproject = tomllib.loads((CONNECTOR_ROOT / "pyproject.toml").read_text())
    return pyproject["tool"]["poetry"]["dependencies"]["python"]


def test_python_floor_is_at_least_3_11():
    floor = re.match(r"\^(\d+)\.(\d+)", _python_constraint())
    assert floor, f"Unexpected python constraint format: {_python_constraint()!r}"
    assert tuple(map(int, floor.groups())) >= (3, 11)


def test_lock_file_matches_python_constraint():
    lock = tomllib.loads((CONNECTOR_ROOT / "poetry.lock").read_text())
    assert lock["metadata"]["python-versions"] == _python_constraint()
