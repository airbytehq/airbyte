# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from unittest import TestCase

from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, TState, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    RootPath,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))

_DOMAIN = "a-domain.freshdesk.com"


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("time_entries", SyncMode.incremental).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _response_template() -> Dict[str, Any]:
    return find_template("time_entries", __file__)


def _record() -> RecordBuilder:
    return create_record_builder(
        _response_template(), RootPath(), record_id_path=FieldPath("id"), record_cursor_path=FieldPath("executed_at")
    )


def _response() -> HttpResponseBuilder:
    return create_response_builder(response_template=_response_template(), records_path=RootPath())


def _read(config_builder: Optional[ConfigBuilder] = None, state_builder: Optional[StateBuilder] = None) -> EntrypointOutput:
    catalog = _catalog()
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state)


class TimeEntriesTest(TestCase):
    @HttpMocker()
    def test_incremental_without_state_starts_at_1970_and_emits_max_cursor(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/time_entries?per_page=100&executed_after=1970-01-01T00%3A00%3A00Z"),
            _response()
            .with_record(_record().with_id(1).with_cursor("2024-03-01T00:00:00Z"))
            .with_record(_record().with_id(2).with_cursor("2024-03-15T00:00:00Z"))
            .build(),
        )

        output = _read(config_builder=ConfigBuilder().domain(_DOMAIN))

        assert len(output.records) == 2
        assert output.most_recent_state.stream_state.__dict__["executed_at"] == "2024-03-15T00:00:00Z"

    @HttpMocker()
    def test_incremental_state_uses_default_14_day_lookback(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/time_entries?per_page=100&executed_after=2024-03-01T00%3A00%3A00Z"),
            _response().with_record(_record().with_id(1).with_cursor("2024-03-15T00:00:00Z")).build(),
        )

        output = _read(
            config_builder=ConfigBuilder().domain(_DOMAIN),
            state_builder=StateBuilder().with_stream_state("time_entries", {"executed_at": "2024-03-15T00:00:00Z"}),
        )

        assert len(output.records) == 1

    @HttpMocker()
    def test_incremental_state_uses_configured_lookback_window(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/time_entries?per_page=100&executed_after=2024-02-14T00%3A00%3A00Z"),
            _response().with_record(_record().with_id(1).with_cursor("2024-03-15T00:00:00Z")).build(),
        )

        output = _read(
            config_builder=ConfigBuilder().domain(_DOMAIN).lookback_window_in_days(30),
            state_builder=StateBuilder().with_stream_state("time_entries", {"executed_at": "2024-03-15T00:00:00Z"}),
        )

        assert len(output.records) == 1
