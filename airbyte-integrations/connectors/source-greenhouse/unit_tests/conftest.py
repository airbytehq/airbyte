# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CONNECTOR_PATH = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_PATH))


@pytest.fixture
def get_source():
    def _get_source(config, state=None):
        return YamlDeclarativeSource(
            path_to_yaml=str(_CONNECTOR_PATH / "manifest.yaml"),
            catalog=CatalogBuilder().build(),
            config=copy.deepcopy(config),
            state=state or StateBuilder().build(),
        )

    return _get_source


@pytest.fixture
def connector_path():
    return _CONNECTOR_PATH
