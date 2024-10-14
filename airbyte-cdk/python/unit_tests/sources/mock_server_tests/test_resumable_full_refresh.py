#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.models import AirbyteStateBlob, AirbyteStreamStatus, ConfiguredAirbyteCatalog, FailureType, SyncMode, Type
from airbyte_cdk.test.catalog_builder import ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    FieldUpdatePaginationStrategy,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
)
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.sources.mock_server_tests.mock_source_fixture import SourceFixture
from unit_tests.sources.mock_server_tests.test_helpers import emits_successful_sync_status_messages, validate_message_order

_NOW = datetime.now(timezone.utc)


class RequestBuilder:
    @classmethod
    def justice_songs_endpoint(cls) -> "RequestBuilder":
        return cls("justice_songs")

    def __init__(self, resource: str) -> None:
        self._resource = resource
        self._page: Optional[int] = None

    def with_page(self, page: int) -> "RequestBuilder":
        self._page = page
        return self

    def build(self) -> HttpRequest:
        query_params = {}
        if self._page:
            query_params["page"] = self._page

        return HttpRequest(
            url=f"https://api.airbyte-test.com/v1/{self._resource}",
            query_params=query_params,
        )


def _create_catalog(names_and_sync_modes: List[tuple[str, SyncMode, Dict[str, Any]]]) -> ConfiguredAirbyteCatalog:
    stream_builder = ConfiguredAirbyteStreamBuilder()
    streams = []
    for stream_name, sync_mode, json_schema in names_and_sync_modes:
        streams.append(stream_builder.with_name(stream_name).with_sync_mode(sync_mode).with_json_schema(json_schema or {}))

    return ConfiguredAirbyteCatalog(streams=list(map(lambda builder: builder.build(), streams)))


def _create_justice_songs_request() -> RequestBuilder:
    return RequestBuilder.justice_songs_endpoint()


RESPONSE_TEMPLATE = {"object": "list", "has_more": False, "data": [{"id": "123", "created_at": "2024-01-01T07:04:28.000Z"}]}


JUSTICE_SONGS_TEMPLATE = {
    "object": "list",
    "has_more": False,
    "data": [
        {
            "id": "cross_01",
            "created_at": "2024-02-01T07:04:28.000Z",
            "name": "Genesis",
            "album": "Cross",
        },
        {
            "id": "hyperdrama_01",
            "created_at": "2024-02-01T07:04:28.000Z",
            "name": "dukes",
            "album": "",
        },
    ],
}


RESOURCE_TO_TEMPLATE = {
    "justice_songs": JUSTICE_SONGS_TEMPLATE,
}


def _create_response(pagination_has_more: bool = False) -> HttpResponseBuilder:
    return create_response_builder(
        response_template=RESPONSE_TEMPLATE,
        records_path=FieldPath("data"),
        pagination_strategy=FieldUpdatePaginationStrategy(FieldPath("has_more"), pagination_has_more),
    )


def _create_record(resource: str) -> RecordBuilder:
    return create_record_builder(
        response_template=RESOURCE_TO_TEMPLATE.get(resource),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created_at"),
    )


@freezegun.freeze_time(_NOW)
class ResumableFullRefreshStreamTest(TestCase):
    @HttpMocker()
    def test_resumable_full_refresh_sync(self, http_mocker):
        config = {}

        http_mocker.get(
            _create_justice_songs_request().build(),
            _create_response(pagination_has_more=True)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        http_mocker.get(
            _create_justice_songs_request().with_page(1).build(),
            _create_response(pagination_has_more=True)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        http_mocker.get(
            _create_justice_songs_request().with_page(2).build(),
            _create_response(pagination_has_more=False).with_pagination().with_record(record=_create_record("justice_songs")).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("justice_songs", SyncMode.full_refresh, {})]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("justice_songs"))
        assert len(actual_messages.records) == 5
        assert len(actual_messages.state_messages) == 4
        validate_message_order(
            [Type.RECORD, Type.RECORD, Type.STATE, Type.RECORD, Type.RECORD, Type.STATE, Type.RECORD, Type.STATE, Type.STATE],
            actual_messages.records_and_state_messages,
        )
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[0].state.stream.stream_state == AirbyteStateBlob(page=1)
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 2.0
        assert actual_messages.state_messages[1].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[1].state.stream.stream_state == AirbyteStateBlob(page=2)
        assert actual_messages.state_messages[1].state.sourceStats.recordCount == 2.0
        assert actual_messages.state_messages[2].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[2].state.stream.stream_state == AirbyteStateBlob(__ab_full_refresh_sync_complete=True)
        assert actual_messages.state_messages[2].state.sourceStats.recordCount == 1.0
        assert actual_messages.state_messages[3].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[3].state.stream.stream_state == AirbyteStateBlob(__ab_full_refresh_sync_complete=True)
        assert actual_messages.state_messages[3].state.sourceStats.recordCount == 0.0

    @HttpMocker()
    def test_resumable_full_refresh_second_attempt(self, http_mocker):
        config = {}

        state = StateBuilder().with_stream_state("justice_songs", {"page": 100}).build()

        http_mocker.get(
            _create_justice_songs_request().with_page(100).build(),
            _create_response(pagination_has_more=True)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        http_mocker.get(
            _create_justice_songs_request().with_page(101).build(),
            _create_response(pagination_has_more=True)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        http_mocker.get(
            _create_justice_songs_request().with_page(102).build(),
            _create_response(pagination_has_more=False)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("justice_songs", SyncMode.full_refresh, {})]), state=state)

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("justice_songs"))
        assert len(actual_messages.records) == 8
        assert len(actual_messages.state_messages) == 4
        validate_message_order(
            [
                Type.RECORD,
                Type.RECORD,
                Type.RECORD,
                Type.STATE,
                Type.RECORD,
                Type.RECORD,
                Type.RECORD,
                Type.STATE,
                Type.RECORD,
                Type.RECORD,
                Type.STATE,
                Type.STATE,
            ],
            actual_messages.records_and_state_messages,
        )
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[0].state.stream.stream_state == AirbyteStateBlob(page=101)
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 3.0
        assert actual_messages.state_messages[1].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[1].state.stream.stream_state == AirbyteStateBlob(page=102)
        assert actual_messages.state_messages[1].state.sourceStats.recordCount == 3.0
        assert actual_messages.state_messages[2].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[2].state.stream.stream_state == AirbyteStateBlob(__ab_full_refresh_sync_complete=True)
        assert actual_messages.state_messages[2].state.sourceStats.recordCount == 2.0
        assert actual_messages.state_messages[3].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[3].state.stream.stream_state == AirbyteStateBlob(__ab_full_refresh_sync_complete=True)
        assert actual_messages.state_messages[3].state.sourceStats.recordCount == 0.0

    @HttpMocker()
    def test_resumable_full_refresh_failure(self, http_mocker):
        config = {}

        http_mocker.get(
            _create_justice_songs_request().build(),
            _create_response(pagination_has_more=True)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        http_mocker.get(
            _create_justice_songs_request().with_page(1).build(),
            _create_response(pagination_has_more=True)
            .with_pagination()
            .with_record(record=_create_record("justice_songs"))
            .with_record(record=_create_record("justice_songs"))
            .build(),
        )

        http_mocker.get(_create_justice_songs_request().with_page(2).build(), _create_response().with_status_code(status_code=400).build())

        source = SourceFixture()
        actual_messages = read(
            source, config=config, catalog=_create_catalog([("justice_songs", SyncMode.full_refresh, {})]), expecting_exception=True
        )

        status_messages = actual_messages.get_stream_statuses("justice_songs")
        assert status_messages[-1] == AirbyteStreamStatus.INCOMPLETE
        assert len(actual_messages.records) == 4
        assert len(actual_messages.state_messages) == 2

        validate_message_order(
            [Type.RECORD, Type.RECORD, Type.STATE, Type.RECORD, Type.RECORD, Type.STATE], actual_messages.records_and_state_messages
        )
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[0].state.stream.stream_state == AirbyteStateBlob(page=1)
        assert actual_messages.state_messages[1].state.stream.stream_descriptor.name == "justice_songs"
        assert actual_messages.state_messages[1].state.stream.stream_state == AirbyteStateBlob(page=2)

        assert actual_messages.errors[0].trace.error.failure_type == FailureType.system_error
        assert actual_messages.errors[0].trace.error.stream_descriptor.name == "justice_songs"
        assert "Bad request" in actual_messages.errors[0].trace.error.message
