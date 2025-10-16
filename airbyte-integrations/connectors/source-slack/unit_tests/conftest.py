#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import os
import sys
from pathlib import Path
from typing import MutableMapping

import pytest

from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
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


def get_source(config, stream_name=None, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name)).build() if stream_name else None
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def get_stream_by_name(stream_name, config, state=None):
    state = StateBuilder().build() if not state else state
    streams = get_source(config, stream_name, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@pytest.fixture(autouse=True)
def conversations_list(requests_mock):
    return requests_mock.register_uri(
        "GET",
        "https://slack.com/api/conversations.list?limit=1000&types=public_channel",
        json={
            "channels": [
                {"id": "airbyte-for-beginners", "name": "airbyte-for-beginners", "is_member": True},
                {"id": "good-reads", "name": "good-reads", "is_member": True},
            ]
        },
    )


def base_config() -> MutableMapping:
    return copy.deepcopy(
        {
            "start_date": "2021-07-22T20:00:00Z",
            "end_date": "2021-07-23T20:00:00Z",
            "lookback_window": 1,
            "join_channels": True,
            "channel_filter": ["airbyte-for-beginners", "good-reads"],
        }
    )


def _token_config() -> MutableMapping:
    config = base_config()
    config.update({"credentials": {"option_title": "API Token Credentials", "api_token": "api-token"}})
    return config


@pytest.fixture
def token_config() -> MutableMapping:
    return _token_config()


def _oauth_config() -> MutableMapping:
    config = base_config()
    config.update(
        {
            "credentials": {
                "option_title": "Default OAuth2.0 authorization",
                "client_id": "client.id",
                "client_secret": "client-secret",
                "access_token": "access-token",
            }
        }
    )
    return config


@pytest.fixture
def oauth_config() -> MutableMapping:
    return _oauth_config()


def _legacy_token_config() -> MutableMapping:
    config = base_config()
    config.update({"api_token": "api-token"})
    return config


@pytest.fixture
def legacy_token_config() -> MutableMapping:
    return _legacy_token_config()


def _invalid_config() -> MutableMapping:
    return base_config()


@pytest.fixture
def invalid_config() -> MutableMapping:
    return _invalid_config()


parametrized_configs = pytest.mark.parametrize(
    "config, is_valid",
    (
        (_token_config(), True),
        (_oauth_config(), True),
        (_invalid_config(), False),
    ),
)


@pytest.fixture
def joined_channel():
    return {
        "id": "C061EG9SL",
        "name": "general",
        "is_channel": True,
        "is_group": False,
        "is_im": False,
        "created": 1449252889,
        "creator": "U061F7AUR",
        "is_archived": False,
        "is_general": True,
        "unlinked": 0,
        "name_normalized": "general",
        "is_shared": False,
        "is_ext_shared": False,
        "is_org_shared": False,
        "pending_shared": [],
        "is_pending_ext_shared": False,
        "is_member": True,
        "is_private": False,
        "is_mpim": False,
        "topic": {"value": "Which widget do you worry about?", "creator": "", "last_set": 0},
        "purpose": {"value": "For widget discussion", "creator": "", "last_set": 0},
        "previous_names": [],
    }


def get_retriever(stream: DefaultStream) -> Retriever:
    return stream._stream_partition_generator._partition_factory._retriever
