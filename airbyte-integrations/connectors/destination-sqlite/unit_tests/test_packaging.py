#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


def test_python_requirement_matches_runtime() -> None:
    connector_dir = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((connector_dir / "pyproject.toml").read_text())
    lockfile = tomllib.loads((connector_dir / "poetry.lock").read_text())

    assert pyproject["tool"]["poetry"]["dependencies"]["python"] == "^3.11,<3.13"
    assert lockfile["metadata"]["python-versions"] == "^3.11,<3.13"
