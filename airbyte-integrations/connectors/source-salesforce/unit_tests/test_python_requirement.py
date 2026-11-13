#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
import tomllib
from packaging.specifiers import SpecifierSet


@pytest.mark.parametrize(
    "version, supported",
    [("3.10.99", False), ("3.11.0", True), ("3.12.0", True), ("3.13.0", True), ("3.14.0", False)],
)
@pytest.mark.parametrize("filename", ["pyproject.toml", "poetry.lock"])
def test_supported_python_versions(filename: str, version: str, supported: bool) -> None:
    with (Path(__file__).resolve().parents[1] / filename).open("rb") as file:
        config = tomllib.load(file)

    requirement = (
        config["tool"]["poetry"]["dependencies"]["python"] if filename == "pyproject.toml" else config["metadata"]["python-versions"]
    )
    assert (version in SpecifierSet(requirement.replace("^", ">="))) is supported
