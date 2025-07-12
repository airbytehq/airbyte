#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
from pathlib import Path

from pytest import fixture

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


@fixture(autouse=True)
def mock_sleep(mocker):
    mocker.patch("time.sleep")


@fixture(scope="session", name="account_id")
def account_id_fixture():
    return "unknown_account"


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


GRAPH_URL = resolve_manifest(source=get_source(config={}, state=None)).record.data["manifest"]["definitions"]["base_requester"]["url_base"]

account_url = f"{GRAPH_URL}/me/accounts?fields=id%2Cinstagram_business_account"


@fixture(name="config")
def config_fixture():
    config = {
        "access_token": "TOKEN",
        "start_date": "2022-03-20T00:00:00",
    }

    return config


def mock_fb_account_response(account_id, some_config, requests_mock):
    account = {"id": "test_id", "instagram_business_account": {"id": "test_id"}}
    requests_mock.register_uri(
        "GET",
        f"{GRAPH_URL}/act_{account_id}/" f"?access_token={some_config['access_token']}&fields=instagram_business_account",
        json=account,
    )
    return {
        "json": {
            "data": [
                {
                    "access_token": "access_token",
                    "category": "Software company",
                    "id": f"act_{account_id}",
                    "paging": {"cursors": {"before": "cursor", "after": "cursor"}},
                    "summary": {"total_count": 1},
                    "status_code": 200,
                }
            ]
        }
    }
