#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
import tomllib
from packaging.specifiers import SpecifierSet


@pytest.mark.parametrize(
    "filename, section, key",
    [("pyproject.toml", ("tool", "poetry", "dependencies"), "python"), ("poetry.lock", ("metadata",), "python-versions")],
)
@pytest.mark.parametrize("version, supported", [("3.10", False), ("3.11", True), ("3.12", True), ("3.13", True), ("3.14", False)])
def test_python_compatibility(filename: str, section: tuple[str, ...], key: str, version: str, supported: bool) -> None:
    with (Path(__file__).parents[1] / filename).open("rb") as config_file:
        config = tomllib.load(config_file)
    for part in section:
        config = config[part]

    constraint = SpecifierSet(config[key].replace("^", ">="))

    assert constraint.contains(version) is supported
