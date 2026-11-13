#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import importlib
from pathlib import Path

import tomllib


CONNECTOR_DIR = Path(__file__).resolve().parent.parent


def test_pyproject_requires_python_3_11_or_newer():
    pyproject = tomllib.loads((CONNECTOR_DIR / "pyproject.toml").read_text())
    assert pyproject["tool"]["poetry"]["dependencies"]["python"] == ">=3.11,<3.13"


def test_poetry_lock_metadata_requires_python_3_11_or_newer():
    lock = tomllib.loads((CONNECTOR_DIR / "poetry.lock").read_text())
    assert lock["metadata"]["python-versions"] == ">=3.11,<3.13"


def test_console_script_entrypoint_is_importable():
    pyproject = tomllib.loads((CONNECTOR_DIR / "pyproject.toml").read_text())
    module_name, func_name = pyproject["tool"]["poetry"]["scripts"]["destination-firestore"].split(":")
    assert callable(getattr(importlib.import_module(module_name), func_name))
