#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


CONNECTOR_ROOT = Path(__file__).resolve().parent.parent


def test_python_constraint_requires_3_11():
    pyproject = tomllib.loads((CONNECTOR_ROOT / "pyproject.toml").read_text())
    assert pyproject["tool"]["poetry"]["dependencies"]["python"] == "^3.11,<3.12"


def test_lock_file_has_no_python_3_10_only_packages():
    lock = tomllib.loads((CONNECTOR_ROOT / "poetry.lock").read_text())
    assert lock["metadata"]["python-versions"] == "^3.11,<3.12"
    locked_names = {package["name"] for package in lock["package"]}
    assert locked_names.isdisjoint({"exceptiongroup", "tomli"})
