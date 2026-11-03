# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from importlib.metadata import metadata

import pytest
from packaging.specifiers import SpecifierSet


@pytest.mark.parametrize("python_version, supported", [("3.10", False), ("3.11", True), ("3.12", False)])
def test_supported_python_versions(python_version: str, supported: bool) -> None:
    requires_python = metadata("destination-deepset")["Requires-Python"]
    assert (python_version in SpecifierSet(requires_python)) is supported
