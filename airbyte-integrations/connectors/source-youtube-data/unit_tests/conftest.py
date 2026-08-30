#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


@pytest.fixture
def http_mocker():
    return None


def get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        catalog=catalog,
        config=config,
        state=state,
    )
