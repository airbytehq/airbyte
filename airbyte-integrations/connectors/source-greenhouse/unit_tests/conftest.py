# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import copy
import sys
from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

_CONNECTOR_PATH = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_PATH))


@pytest.fixture
def get_source():
    def _get_source(config, state=None):
        manifest = yaml.safe_load((_CONNECTOR_PATH / "manifest.yaml").read_text())
        manifest.pop("advanced_auth")
        return ConcurrentDeclarativeSource(
            catalog=CatalogBuilder().build(),
            config=copy.deepcopy(config),
            state=state or StateBuilder().build(),
            source_config=manifest,
        )

    return _get_source
