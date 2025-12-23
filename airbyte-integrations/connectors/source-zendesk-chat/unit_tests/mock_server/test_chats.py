# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from unittest import TestCase

from config_builder import ConfigBuilder
from pagination_strategy import ZendeskChatPaginationStrategy

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
_STREAM_NAME = "chats"
_SUBDOMAIN = "a_subdomain"
_START_DATETIME = datetime(2015, 10, 1, tzinfo=timezone.utc)
_NEXT_PAGE_URL = f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/chats?fields=chats%28%2A%29&limit=1000&some_page_information=a_pagination_cursor_value"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _response_template() -> Dict[str, Any]:
    return find_template(_STREAM_NAME, __file__)


def _record() -> RecordBuilder:
    return create_record_builder(
        _response_template(), FieldPath(_STREAM_NAME), record_id_path=FieldPath("id"), record_cursor_path=FieldPath("update_timestamp")
    )


def _response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=_response_template(),
        records_path=FieldPath(_STREAM_NAME),
        pagination_strategy=ZendeskChatPaginationStrategy("chats", _NEXT_PAGE_URL),
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


class ChatsTest(TestCase):
    @HttpMocker()
    def test_when_read_then_extract_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/chats?fields=chats%28%2A%29&limit=1000&start_time={int(_START_DATETIME.timestamp())}"
            ),
            _response().with_record(_record()).with_record(_record()).build(),
        )
        output = read(ConfigBuilder().start_date(_START_DATETIME).subdomain(_SUBDOMAIN), StateBuilder())
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_count_is_1000_when_read_then_paginate(self, http_mocker: HttpMocker) -> None:
        response_with_1000_records = _response()
        for i in range(0, 1000):
            response_with_1000_records.with_record(_record())
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/chats?fields=chats%28%2A%29&limit=1000&start_time={int(_START_DATETIME.timestamp())}"
            ),
            response_with_1000_records.with_pagination().build(),
        )
        http_mocker.get(
            HttpRequest(_NEXT_PAGE_URL),
            _response().with_record(_record()).build(),
        )

        output = read(ConfigBuilder().start_date(_START_DATETIME).subdomain(_SUBDOMAIN), StateBuilder())

        assert len(output.records) == 1001
