#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


CONNECTOR_DIR = Path(__file__).parent.parent
PYTHON_VERSION = "^3.11,<3.12"


def test_pyproject_requires_python_311():
    with (CONNECTOR_DIR / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    assert pyproject["tool"]["poetry"]["dependencies"]["python"] == PYTHON_VERSION


def test_poetry_lock_is_locked_for_python_311():
    with (CONNECTOR_DIR / "poetry.lock").open("rb") as lock_file:
        lock = tomllib.load(lock_file)

    assert lock["metadata"]["python-versions"] == PYTHON_VERSION
