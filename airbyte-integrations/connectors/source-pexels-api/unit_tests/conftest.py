# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture
def manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture
def source() -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH))
