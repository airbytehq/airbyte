# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import tomllib
from packaging.specifiers import SpecifierSet


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]


def test_python_constraint() -> None:
    pyproject = tomllib.loads((CONNECTOR_ROOT / "pyproject.toml").read_text())
    constraint = pyproject["tool"]["poetry"]["dependencies"]["python"]
    supported_versions = SpecifierSet(constraint.replace("^", ">="))

    assert "3.10" not in supported_versions
    assert "3.11" in supported_versions


def test_lock_has_no_python_310_markers() -> None:
    lock = tomllib.loads((CONNECTOR_ROOT / "poetry.lock").read_text())

    for package in lock["package"]:
        assert 'python_version == "3.10"' not in package.get("markers", "")
