#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import Mock

import pytest

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components

BASE_CONFIG = {
    "start_date": "2021-01-01T00:00:00Z",
    "credentials": {"auth_type": "access_token", "access_token": "token"},
}
GROUPS_LIST_URL = "https://gitlab.com/api/v4/groups?per_page=50"


@pytest.fixture()
def config():
    return BASE_CONFIG


@pytest.fixture()
def oauth_config():
    return BASE_CONFIG | {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "access_token": "access_token",
            "token_expiry_date": "2023-01-01T00:00:00Z",
            "refresh_token": "refresh_token",
        },
    }


@pytest.fixture
def config_with_project_groups():
    return BASE_CONFIG | {"groups_list": ["g1"], "projects_list": ["p1"]}


def get_source(config: Mapping[str, Any], config_path: str = None) -> YamlDeclarativeSource:
    state = StateBuilder().build()
    catalog = CatalogBuilder().build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(_YAML_FILE_PATH),
        config=config,
        state=state,
        catalog=catalog,
        config_path=config_path,
    )
    source.write_config = Mock()
    return source


def get_stream_by_name(source: YamlDeclarativeSource, stream_name: str, config: Mapping[str, Any]) -> Stream:
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]
