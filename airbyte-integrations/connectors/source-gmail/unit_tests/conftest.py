#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Any, Mapping, Optional

import pytest
import yaml

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="session")
def manifest() -> Mapping[str, Any]:
    with open(_MANIFEST_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture
def base_config() -> Mapping[str, Any]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "client_refresh_token": "test_refresh_token",
        "include_spam_and_trash": False,
    }


@pytest.fixture
def config_with_start_date(base_config) -> Mapping[str, Any]:
    return {**base_config, "start_date": "2024-01-01T00:00:00Z"}


def build_source(config: Mapping[str, Any], state: Optional[list] = None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)


@pytest.fixture(autouse=True)
def mock_oauth(requests_mock):
    requests_mock.post(
        "https://accounts.google.com/o/oauth2/token",
        json={"access_token": "access_token", "expires_in": 3600},
    )
