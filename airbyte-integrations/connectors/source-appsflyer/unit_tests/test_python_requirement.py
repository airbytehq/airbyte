# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import tomllib


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_requires_python_3_11_or_newer():
    pyproject = tomllib.loads((CONNECTOR_ROOT / "pyproject.toml").read_text())
    assert pyproject["tool"]["poetry"]["dependencies"]["python"] == "^3.11,<3.14"


def test_lock_file_requires_python_3_11_or_newer():
    lock = tomllib.loads((CONNECTOR_ROOT / "poetry.lock").read_text())
    assert lock["metadata"]["python-versions"] == "^3.11,<3.14"
