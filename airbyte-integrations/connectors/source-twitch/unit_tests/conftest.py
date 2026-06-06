# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

import os
import sys
from copy import deepcopy
from pathlib import Path

from pytest import fixture

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def get_source(config, state=None, config_path=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state, config_path=config_path)


def find_stream(stream_name, config, state=None):
    state = StateBuilder().build() if not state else state
    streams = get_source(config, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@fixture(name="config")
def config_fixture():
    return {
        "client_id": "client_id",
        "client_secret": "client_secret",
        "client_refresh_token": "refresh_token",
        "login": ["airbyte"],
        "start_date": "2026-05-05T00:00:00Z",
        "custom_reports": {
            "clips": [
                {
                    "name": "Top Clips",
                    "game_name": "Fortnite",
                    "is_featured": True,
                }
            ],
            "videos": [
                {
                    "name": "Top Vods",
                    "game_name": "Fortnite",
                    "language": "en",
                    "period": "week",
                    "sort": "views",
                    "type": "archive",
                }
            ],
        },
    }


@fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner
