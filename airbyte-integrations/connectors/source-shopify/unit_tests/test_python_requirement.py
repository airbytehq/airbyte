#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import tomllib


def test_python_requirement() -> None:
    connector_directory = Path(__file__).resolve().parents[1]
    with (connector_directory / "pyproject.toml").open("rb") as project_file:
        project = tomllib.load(project_file)
    with (connector_directory / "poetry.lock").open("rb") as lock_file:
        lock = tomllib.load(lock_file)

    requirement = project["tool"]["poetry"]["dependencies"]["python"]
    assert requirement == "^3.11,<3.14"
    assert lock["metadata"]["python-versions"] == requirement
