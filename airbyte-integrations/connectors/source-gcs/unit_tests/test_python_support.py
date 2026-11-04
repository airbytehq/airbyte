# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import tomllib


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("filename", ["pyproject.toml", "poetry.lock"])
def test_python_support_range(filename: str) -> None:
    with (CONNECTOR_ROOT / filename).open("rb") as file:
        config = tomllib.load(file)

    constraint = (
        config["tool"]["poetry"]["dependencies"]["python"] if filename == "pyproject.toml" else config["metadata"]["python-versions"]
    )
    assert constraint == "^3.11,<3.14"
