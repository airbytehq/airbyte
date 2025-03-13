# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
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

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("segments", SyncMode.full_refresh).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _response_template() -> Dict[str, Any]:
    return find_template("segments", __file__)


def _record() -> RecordBuilder:
    return create_record_builder(
        _response_template(), FieldPath("segments"), record_id_path=FieldPath("id"), record_cursor_path=FieldPath("updated_at")
    )


def _response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=_response_template(),
        records_path=FieldPath("segments"),
    )


def read(
    config_builder: Optional[ConfigBuilder] = None,
    state_builder: Optional[StateBuilder] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = _catalog()
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state, expecting_exception)


class SegmentsTest(TestCase):
    @HttpMocker()
    def test_when_read_then_extract_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest("https://api.intercom.io/segments", query_params={"per_page": "150"}),
            _response().with_record(_record()).with_record(_record()).build(),
        )
        output = read(ConfigBuilder(), StateBuilder())
        assert len(output.records) == 2
