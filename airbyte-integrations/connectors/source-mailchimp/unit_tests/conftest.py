#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path

from pytest import fixture

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
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


def get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def find_stream(stream_name, config, state=None):
    state = StateBuilder().build() if not state else state
    streams = get_source(config, state).streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@fixture(name="data_center")
def data_center_fixture():
    return "some_dc"


@fixture(name="config")
def config_fixture(data_center):
    return {"apikey": f"API_KEY-{data_center}", "start_date": "2022-01-01T00:00:00.000Z"}


@fixture(name="access_token")
def access_token_fixture():
    return "some_access_token"


@fixture(name="oauth_config")
def oauth_config_fixture(access_token):
    return {
        "credentials": {
            "auth_type": "oauth2.0",
            "client_id": "111111111",
            "client_secret": "secret_1111111111",
            "access_token": access_token,
        }
    }


@fixture(name="apikey_config")
def apikey_config_fixture(data_center):
    return {"credentials": {"auth_type": "apikey", "apikey": f"some_api_key-{data_center}"}}


@fixture(name="wrong_config")
def wrong_config_fixture():
    return {"credentials": {"auth_type": "not auth_type"}}
