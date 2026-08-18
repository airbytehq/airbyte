# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CONNECTOR_PATH = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_PATH))


class LocalYamlDeclarativeSource(YamlDeclarativeSource):
    def _read_and_parse_yaml_file(self, path_to_yaml_file):
        return self._parse(Path(path_to_yaml_file).read_text())


@pytest.fixture
def get_source():
    def _get_source(config, state=None):
        return LocalYamlDeclarativeSource(
            path_to_yaml=str(_CONNECTOR_PATH / "manifest.yaml"),
            catalog=CatalogBuilder().build(),
            config=config,
            state=state or StateBuilder().build(),
        )

    return _get_source
