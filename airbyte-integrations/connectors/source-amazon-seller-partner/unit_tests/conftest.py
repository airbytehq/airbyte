# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import sys
from pathlib import Path
from typing import Any, Mapping

import pytest
from pytest_mock import mocker

from airbyte_cdk import NoAuth, Stream, YamlDeclarativeSource
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


def get_source(config, state=None, config_path=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state, config_path=config_path)


def get_stream_by_name(name: str, config: dict) -> Stream:
    source = get_source(config)
    for stream in source.streams(config):
        if stream.name == name:
            return stream


@pytest.fixture
def init_kwargs() -> Mapping[str, Any]:
    return {
        "url_base": "https://test.url",
        "replication_start_date": "2022-09-01T00:00:00Z",
        "marketplace_id": "market",
        "period_in_days": 90,
        "report_options": None,
        "replication_end_date": None,
    }


@pytest.fixture
def report_init_kwargs(init_kwargs) -> Mapping[str, Any]:
    return {"stream_name": "GET_TEST_REPORT", "authenticator": NoAuth({}), **init_kwargs}


@pytest.fixture
def http_mocker() -> None:
    """This fixture is needed to pass http_mocker parameter from the @HttpMocker decorator to a test"""


@pytest.fixture(autouse=True)
def time_mocker(mocker) -> None:
    mocker.patch("time.sleep", lambda x: None)
