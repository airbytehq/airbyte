#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


def test_python_requirement_matches_lock() -> None:
    connector_path = Path(__file__).parents[1]
    project = tomllib.loads((connector_path / "pyproject.toml").read_text())
    lock = tomllib.loads((connector_path / "poetry.lock").read_text())

    assert project["tool"]["poetry"]["dependencies"]["python"] == "^3.11,<3.12"
    assert lock["metadata"]["python-versions"] == "^3.11,<3.12"
