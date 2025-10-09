# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

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
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
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


PAGE_LIMIT_300TH_REACHED = '{"description":"Validation failed","errors":[{"field":"page","message":"You cannot access tickets beyond the 300th page. Please provide a smaller page number.","code":"invalid_value"}]}'


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components

_DOMAIN = "a-domain.freshdesk.com"
_API_KEY = "an_api_key"


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("tickets", SyncMode.full_refresh).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _response_template() -> Dict[str, Any]:
    return find_template("tickets", __file__)


def _record() -> RecordBuilder:
    return create_record_builder(
        _response_template(), RootPath(), record_id_path=FieldPath("id"), record_cursor_path=FieldPath("updated_at")
    )


def _response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=_response_template(),
        records_path=RootPath(),
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


class TicketsTest(TestCase):
    @HttpMocker()
    def test_when_read_then_extract_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                f"https://{_DOMAIN}/api/v2/tickets?order_type=asc&order_by=updated_at&include=description,requester,stats&per_page=100&updated_since=2022-01-01T00%3A00%3A00Z"
            ),
            _response().with_record(_record()).with_record(_record()).build(),
        )
        output = read(ConfigBuilder().domain(_DOMAIN).start_date(datetime(2022, 1, 1)), StateBuilder())
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_hitting_300th_page_when_read_then_reset_pagination(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                f"https://{_DOMAIN}/api/v2/tickets?order_type=asc&order_by=updated_at&include=description,requester,stats&per_page=100&updated_since=2022-01-01T00%3A00%3A00Z"
            ),
            self._a_response_with_full_page("2023-01-01T00:00:00Z"),
        )
        for page in range(2, 301):
            http_mocker.get(
                HttpRequest(
                    f"https://{_DOMAIN}/api/v2/tickets?order_type=asc&order_by=updated_at&include=description,requester,stats&page={page}&per_page=100&updated_since=2022-01-01T00%3A00%3A00Z"
                ),
                self._a_response_with_full_page("2023-01-01T00:00:00Z"),
            )
        http_mocker.get(
            HttpRequest(
                f"https://{_DOMAIN}/api/v2/tickets?order_type=asc&order_by=updated_at&include=description,requester,stats&page=301&per_page=100&updated_since=2022-01-01T00%3A00%3A00Z"
            ),
            HttpResponse(PAGE_LIMIT_300TH_REACHED, 400),
        )

        http_mocker.get(
            HttpRequest(
                f"https://{_DOMAIN}/api/v2/tickets?order_type=asc&order_by=updated_at&include=description,requester,stats&per_page=100&updated_since=2023-01-01T00%3A00%3A00Z"
            ),
            _response().with_record(_record()).with_record(_record()).build(),
        )

        output = read(ConfigBuilder().domain(_DOMAIN).start_date(datetime(2022, 1, 1)), StateBuilder())

        assert len(output.records) == 300 * 100 + 2

    def _a_response_with_full_page(self, cursor_value: str) -> HttpResponse:
        response = _response()
        for x in range(100):
            response.with_record(_record().with_cursor(cursor_value))
        return response.build()
