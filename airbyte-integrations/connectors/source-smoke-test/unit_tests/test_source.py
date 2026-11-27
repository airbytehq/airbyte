# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import tomllib
from packaging.specifiers import SpecifierSet

from airbyte.cli.smoke_test_source.source import SourceSmokeTest


def test_python_requirement_excludes_3_10():
    pyproject = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    python_requirement = SpecifierSet(pyproject["tool"]["poetry"]["dependencies"]["python"])

    assert "3.10" not in python_requirement
    assert "3.11" in python_requirement
    assert "3.12" in python_requirement
    assert "3.13" not in python_requirement


def test_spec():
    spec = SourceSmokeTest().spec(logging.getLogger("airbyte"))
    connection_specification = spec.connectionSpecification

    assert isinstance(connection_specification, dict)
    assert connection_specification
    assert "properties" in connection_specification
