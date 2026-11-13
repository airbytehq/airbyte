#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


CONNECTOR_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PYTHON_CONSTRAINT = "^3.11,<3.12"


def _load_toml(filename: str) -> dict:
    return tomllib.loads((CONNECTOR_ROOT / filename).read_text())


def test_pyproject_requires_python_3_11_or_newer():
    python_constraint = _load_toml("pyproject.toml")["tool"]["poetry"]["dependencies"]["python"]
    assert python_constraint == EXPECTED_PYTHON_CONSTRAINT


def test_poetry_lock_matches_pyproject_python_constraint():
    lock_metadata = _load_toml("poetry.lock")["metadata"]
    assert lock_metadata["python-versions"] == EXPECTED_PYTHON_CONSTRAINT
