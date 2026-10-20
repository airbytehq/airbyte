#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import re
from pathlib import Path

import yaml
from packaging.specifiers import SpecifierSet
from packaging.version import Version


CONNECTOR_DIR = Path(__file__).parent.parent
# python-connector-base 4.1.x ships Python 3.13.
BASE_IMAGE_PYTHON_VERSION = "3.13"


def _python_constraint() -> SpecifierSet:
    pyproject = (CONNECTOR_DIR / "pyproject.toml").read_text()
    constraint = re.search(r'^python = "([^"]+)"', pyproject, re.MULTILINE).group(1)
    # Poetry caret "^X.Y" lower bound is ">=X.Y"; its implicit "<X+1" upper bound does not affect 3.x checks.
    return SpecifierSet(constraint.replace("^", ">="))


def test_python_constraint_allows_base_image_python_version():
    assert BASE_IMAGE_PYTHON_VERSION in _python_constraint()


def test_base_image_ships_supported_python_version():
    metadata = yaml.safe_load((CONNECTOR_DIR / "metadata.yaml").read_text())
    base_image = metadata["data"]["connectorBuildOptions"]["baseImage"]
    base_image_version = Version(re.search(r"python-connector-base:([\d.]+)@", base_image).group(1))
    assert base_image_version >= Version("4.1.0")
