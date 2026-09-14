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
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
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


def _catalog(sync_mode: SyncMode = SyncMode.full_refresh) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


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
    sync_mode: SyncMode = SyncMode.full_refresh,
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state, expecting_exception)


class ChatsTest(TestCase):
    @HttpMocker()
    def test_404_error_is_ignored(self, http_mocker: HttpMocker) -> None:
        """Test that 404 errors are ignored per manifest error handler."""
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/chats?fields=chats%28%2A%29&limit=1000&start_time={int(_START_DATETIME.timestamp())}"
            ),
            HttpResponse(body='{"error": "Not Found"}', status_code=404),
        )

        output = read(ConfigBuilder().start_date(_START_DATETIME).subdomain(_SUBDOMAIN), StateBuilder())

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

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
        """Test pagination when count reaches 1000 records.

        NOTE: This test validates next_page URL pagination which is also used by the 'agent_timeline' stream.
        Both streams use the same DefaultPaginator configuration with RequestPath page_token_option,
        so this test provides pagination coverage for both streams.

        The record count assertion uses == for exact matching. The records are generated from templates
        with the same ID, so we verify the total count rather than unique IDs. The pagination behavior
        (fetching page 2 when page 1 has 1000 records) is the key validation here.
        """
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
        # Verify records have expected structure (id field exists from template)
        assert all("id" in r.record.data for r in output.records)

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync without prior state (first sync).

        Uses DatetimeBasedCursor with cursor_field: update_timestamp and datetime_format: %s.
        The start_time request parameter uses the config's start_date converted to epoch seconds.
        The state stores the cursor value as epoch seconds string.
        """
        update_timestamp_1 = "1609459200"
        update_timestamp_2 = "1609462800"
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/chats?fields=chats%28%2A%29&limit=1000&start_time={int(_START_DATETIME.timestamp())}"
            ),
            _response()
            .with_record(_record().with_field(FieldPath("update_timestamp"), update_timestamp_1))
            .with_record(_record().with_field(FieldPath("update_timestamp"), update_timestamp_2))
            .build(),
        )

        output = read(
            ConfigBuilder().start_date(_START_DATETIME).subdomain(_SUBDOMAIN),
            StateBuilder(),
            sync_mode=SyncMode.incremental,
        )

        assert len(output.records) == 2
        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state
        assert latest_state.__dict__["update_timestamp"] == update_timestamp_2

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with prior state (second sync).

        When state has update_timestamp cursor, the request uses that value for the start_time parameter.
        Both state and request parameter use epoch seconds format.
        """
        prior_cursor_seconds = "1609459200"
        new_update_timestamp = "1609466400"
        http_mocker.get(
            HttpRequest(
                f"https://{_SUBDOMAIN}.zendesk.com/api/v2/chat/incremental/chats?fields=chats%28%2A%29&limit=1000&start_time={prior_cursor_seconds}"
            ),
            _response().with_record(_record().with_field(FieldPath("update_timestamp"), new_update_timestamp)).build(),
        )

        output = read(
            ConfigBuilder().start_date(_START_DATETIME).subdomain(_SUBDOMAIN),
            StateBuilder().with_stream_state(_STREAM_NAME, {"update_timestamp": prior_cursor_seconds}),
            sync_mode=SyncMode.incremental,
        )

        assert len(output.records) == 1
        latest_state = output.most_recent_state.stream_state
        assert latest_state.__dict__["update_timestamp"] == new_update_timestamp
