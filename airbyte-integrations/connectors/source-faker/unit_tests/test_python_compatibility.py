# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from importlib.metadata import version
from pathlib import Path

import tomllib
from packaging.specifiers import SpecifierSet
from packaging.version import Version


def test_python_constraint_allows_python_313():
    pyproject_path = Path(__file__).parents[1] / "pyproject.toml"
    with pyproject_path.open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    constraint = pyproject["tool"]["poetry"]["dependencies"]["python"]
    spec = SpecifierSet(constraint.replace(" ", ""))

    assert spec.contains(Version("3.13.0"))


def test_airbyte_cdk_major_version_supports_python_313():
    assert int(version("airbyte-cdk").split(".")[0]) >= 7
