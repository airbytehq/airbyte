#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from unittest import TestCase

import freezegun
import pytest
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
)
from airbyte_protocol.models import AirbyteStreamStatus
from unit_tests.sources.mock_server_tests.mock_source_fixture import SourceFixture

_NOW = datetime.now(timezone.utc)


class RequestBuilder:
    @classmethod
    def dividers_endpoint(cls) -> "RequestBuilder":
        return cls("dividers")

    @classmethod
    def legacies_endpoint(cls) -> "RequestBuilder":
        return cls("legacies")

    @classmethod
    def planets_endpoint(cls) -> "RequestBuilder":
        return cls("planets")

    @classmethod
    def users_endpoint(cls) -> "RequestBuilder":
        return cls("users")

    def __init__(self, resource: str) -> None:
        self._resource = resource
        self._start_date: Optional[datetime] = None
        self._end_date: Optional[datetime] = None
        self._category: Optional[str] = None

    def with_start_date(self, start_date: datetime) -> "RequestBuilder":
        self._start_date = start_date
        return self

    def with_end_date(self, end_date: datetime) -> "RequestBuilder":
        self._end_date = end_date
        return self

    def with_category(self, category: str) -> "RequestBuilder":
        self._category = category
        return self

    def build(self) -> HttpRequest:
        query_params = {}
        if self._start_date:
            query_params["start_date"] = self._start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        if self._end_date:
            query_params["end_date"] = self._end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        if self._category:
            query_params["category"] = self._category

        return HttpRequest(
            url=f"https://api.airbyte-test.com/v1/{self._resource}",
            query_params=query_params,
        )


def _create_catalog(names_and_sync_modes: List[tuple[str, SyncMode]]) -> ConfiguredAirbyteCatalog:
    catalog_builder = CatalogBuilder()
    for stream_name, sync_mode in names_and_sync_modes:
        catalog_builder.with_stream(name=stream_name, sync_mode=sync_mode)
    return catalog_builder.build()


def _create_dividers_request() -> RequestBuilder:
    return RequestBuilder.dividers_endpoint()


def _create_legacies_request() -> RequestBuilder:
    return RequestBuilder.legacies_endpoint()


def _create_planets_request() -> RequestBuilder:
    return RequestBuilder.planets_endpoint()


def _create_users_request() -> RequestBuilder:
    return RequestBuilder.users_endpoint()


RESPONSE_TEMPLATE = {
    "object": "list",
    "has_more": False,
    "data": [
        {
            "id": "123",
            "created_at": "2024-01-01T07:04:28.000Z"
        }
    ]
}

USER_TEMPLATE = {
    "object": "list",
    "has_more": False,
    "data": [
        {
            "id": "123",
            "created_at": "2024-01-01T07:04:28",
            "first_name": "Paul",
            "last_name": "Atreides",
        }
    ]
}

PLANET_TEMPLATE = {
    "object": "list",
    "has_more": False,
    "data": [
        {
            "id": "456",
            "created_at": "2024-01-01T07:04:28.000Z",
            "name": "Giedi Prime",
        }
    ]
}

LEGACY_TEMPLATE = {
    "object": "list",
    "has_more": False,
    "data": [
        {
            "id": "l3g4cy",
            "created_at": "2024-02-01T07:04:28.000Z",
            "quote": "What do you leave behind?",
        }
    ]
}

DIVIDER_TEMPLATE = {
    "object": "list",
    "has_more": False,
    "data": [
        {
            "id": "l3t0",
            "created_at": "2024-02-01T07:04:28.000Z",
            "divide_category": "dukes",
        }
    ]
}


RESOURCE_TO_TEMPLATE = {
    "dividers": DIVIDER_TEMPLATE,
    "legacies": LEGACY_TEMPLATE,
    "planets": PLANET_TEMPLATE,
    "users": USER_TEMPLATE,
}


def _create_response() -> HttpResponseBuilder:
    return create_response_builder(
        response_template=RESPONSE_TEMPLATE,
        records_path=FieldPath("data"),
    )


def _create_record(resource: str) -> RecordBuilder:
    return create_record_builder(
        response_template=RESOURCE_TO_TEMPLATE.get(resource),
        records_path=FieldPath("data"),
        record_id_path=FieldPath("id"),
        record_cursor_path=FieldPath("created_at"),
    )


class FullRefreshStreamTest(TestCase):
    @HttpMocker()
    def test_full_refresh_sync(self, http_mocker):
        start_datetime = _NOW - timedelta(days=14)
        config = {
            "start_date": start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        http_mocker.get(
            _create_users_request().build(),
            _create_response().with_record(record=_create_record("users")).with_record(record=_create_record("users")).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("users", SyncMode.full_refresh)]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("users"))
        assert len(actual_messages.records) == 2
        assert len(actual_messages.state_messages) == 1
        validate_message_order([Type.RECORD, Type.RECORD, Type.STATE], actual_messages.records_and_state_messages)
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "users"
        assert actual_messages.state_messages[0].state.stream.stream_state == {"__ab_full_refresh_state_message": True}
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 2.0

    @HttpMocker()
    def test_full_refresh_with_slices(self, http_mocker):
        start_datetime = _NOW - timedelta(days=14)
        config = {
            "start_date": start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        http_mocker.get(
            _create_dividers_request().with_category("dukes").build(),
            _create_response().with_record(record=_create_record("dividers")).with_record(record=_create_record("dividers")).build(),
        )

        http_mocker.get(
            _create_dividers_request().with_category("mentats").build(),
            _create_response().with_record(record=_create_record("dividers")).with_record(record=_create_record("dividers")).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("dividers", SyncMode.full_refresh)]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("dividers"))
        assert len(actual_messages.records) == 4
        assert len(actual_messages.state_messages) == 1
        validate_message_order([Type.RECORD, Type.RECORD, Type.RECORD, Type.RECORD, Type.STATE], actual_messages.records_and_state_messages)
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "dividers"
        assert actual_messages.state_messages[0].state.stream.stream_state == {"__ab_full_refresh_state_message": True}
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 4.0


@freezegun.freeze_time(_NOW)
class IncrementalStreamTest(TestCase):
    @HttpMocker()
    def test_incremental_sync(self, http_mocker):
        start_datetime = _NOW - timedelta(days=14)
        config = {
            "start_date": start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        last_record_date_0 = (start_datetime + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_planets_request().with_start_date(start_datetime).with_end_date(start_datetime + timedelta(days=7)).build(),
            _create_response().with_record(record=_create_record("planets").with_cursor(last_record_date_0)).with_record(record=_create_record("planets").with_cursor(last_record_date_0)).with_record(record=_create_record("planets").with_cursor(last_record_date_0)).build(),
        )

        last_record_date_1 = (_NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_planets_request().with_start_date(start_datetime + timedelta(days=7)).with_end_date(_NOW).build(),
            _create_response().with_record(record=_create_record("planets").with_cursor(last_record_date_1)).with_record(record=_create_record("planets").with_cursor(last_record_date_1)).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("planets", SyncMode.incremental)]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("planets"))
        assert len(actual_messages.records) == 5
        assert len(actual_messages.state_messages) == 2
        validate_message_order([Type.RECORD, Type.RECORD, Type.RECORD, Type.STATE, Type.RECORD, Type.RECORD, Type.STATE], actual_messages.records_and_state_messages)
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "planets"
        assert actual_messages.state_messages[0].state.stream.stream_state == {"created_at": last_record_date_0}
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 3.0
        assert actual_messages.state_messages[1].state.stream.stream_descriptor.name == "planets"
        assert actual_messages.state_messages[1].state.stream.stream_state == {"created_at": last_record_date_1}
        assert actual_messages.state_messages[1].state.sourceStats.recordCount == 2.0

    @HttpMocker()
    def test_incremental_running_as_full_refresh(self, http_mocker):
        start_datetime = _NOW - timedelta(days=14)
        config = {
            "start_date": start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        last_record_date_0 = (start_datetime + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_planets_request().with_start_date(start_datetime).with_end_date(start_datetime + timedelta(days=7)).build(),
            _create_response().with_record(record=_create_record("planets").with_cursor(last_record_date_0)).with_record(record=_create_record("planets").with_cursor(last_record_date_0)).with_record(record=_create_record("planets").with_cursor(last_record_date_0)).build(),
        )

        last_record_date_1 = (_NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_planets_request().with_start_date(start_datetime + timedelta(days=7)).with_end_date(_NOW).build(),
            _create_response().with_record(record=_create_record("planets").with_cursor(last_record_date_1)).with_record(record=_create_record("planets").with_cursor(last_record_date_1)).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("planets", SyncMode.full_refresh)]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("planets"))
        assert len(actual_messages.records) == 5
        assert len(actual_messages.state_messages) == 1
        validate_message_order([Type.RECORD, Type.RECORD, Type.RECORD, Type.RECORD, Type.RECORD, Type.STATE], actual_messages.records_and_state_messages)
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "planets"
        assert actual_messages.state_messages[0].state.stream.stream_state == {"created_at": last_record_date_1}
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 5.0

    @HttpMocker()
    def test_legacy_incremental_sync(self, http_mocker):
        start_datetime = _NOW - timedelta(days=14)
        config = {
            "start_date": start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        last_record_date_0 = (start_datetime + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_legacies_request().with_start_date(start_datetime).with_end_date(start_datetime + timedelta(days=7)).build(),
            _create_response().with_record(record=_create_record("legacies").with_cursor(last_record_date_0)).with_record(record=_create_record("legacies").with_cursor(last_record_date_0)).with_record(record=_create_record("legacies").with_cursor(last_record_date_0)).build(),
        )

        last_record_date_1 = (_NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_legacies_request().with_start_date(start_datetime + timedelta(days=7)).with_end_date(_NOW).build(),
            _create_response().with_record(record=_create_record("legacies").with_cursor(last_record_date_1)).with_record(record=_create_record("legacies").with_cursor(last_record_date_1)).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("legacies", SyncMode.incremental)]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("legacies"))
        assert len(actual_messages.records) == 5
        assert len(actual_messages.state_messages) == 2
        validate_message_order([Type.RECORD, Type.RECORD, Type.RECORD, Type.STATE, Type.RECORD, Type.RECORD, Type.STATE], actual_messages.records_and_state_messages)
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "legacies"
        assert actual_messages.state_messages[0].state.stream.stream_state == {"created_at": last_record_date_0}
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 3.0
        assert actual_messages.state_messages[1].state.stream.stream_descriptor.name == "legacies"
        assert actual_messages.state_messages[1].state.stream.stream_state == {"created_at": last_record_date_1}
        assert actual_messages.state_messages[1].state.sourceStats.recordCount == 2.0


@freezegun.freeze_time(_NOW)
class MultipleStreamTest(TestCase):
    @HttpMocker()
    def test_incremental_and_full_refresh_streams(self, http_mocker):
        start_datetime = _NOW - timedelta(days=14)
        config = {
            "start_date": start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        # Mocks for users full refresh stream
        http_mocker.get(
            _create_users_request().build(),
            _create_response().with_record(record=_create_record("users")).with_record(record=_create_record("users")).build(),
        )

        # Mocks for planets incremental stream
        last_record_date_0 = (start_datetime + timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_planets_request().with_start_date(start_datetime).with_end_date(start_datetime + timedelta(days=7)).build(),
            _create_response().with_record(record=_create_record("planets").with_cursor(last_record_date_0)).with_record(record=_create_record("planets").with_cursor(last_record_date_0)).with_record(record=_create_record("planets").with_cursor(last_record_date_0)).build(),
        )

        last_record_date_1 = (_NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        http_mocker.get(
            _create_planets_request().with_start_date(start_datetime + timedelta(days=7)).with_end_date(_NOW).build(),
            _create_response().with_record(record=_create_record("planets").with_cursor(last_record_date_1)).with_record(record=_create_record("planets").with_cursor(last_record_date_1)).build(),
        )

        # Mocks for dividers full refresh stream
        http_mocker.get(
            _create_dividers_request().with_category("dukes").build(),
            _create_response().with_record(record=_create_record("dividers")).with_record(record=_create_record("dividers")).build(),
        )

        http_mocker.get(
            _create_dividers_request().with_category("mentats").build(),
            _create_response().with_record(record=_create_record("dividers")).with_record(record=_create_record("dividers")).build(),
        )

        source = SourceFixture()
        actual_messages = read(source, config=config, catalog=_create_catalog([("users", SyncMode.full_refresh), ("planets", SyncMode.incremental), ("dividers", SyncMode.full_refresh)]))

        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("users"))
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("planets"))
        assert emits_successful_sync_status_messages(actual_messages.get_stream_statuses("dividers"))

        assert len(actual_messages.records) == 11
        assert len(actual_messages.state_messages) == 4
        validate_message_order([
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
            Type.RECORD,
            Type.RECORD,
            Type.RECORD,
            Type.RECORD,
            Type.STATE
        ], actual_messages.records_and_state_messages)
        assert actual_messages.state_messages[0].state.stream.stream_descriptor.name == "users"
        assert actual_messages.state_messages[0].state.stream.stream_state == {"__ab_full_refresh_state_message": True}
        assert actual_messages.state_messages[0].state.sourceStats.recordCount == 2.0
        assert actual_messages.state_messages[1].state.stream.stream_descriptor.name == "planets"
        assert actual_messages.state_messages[1].state.stream.stream_state == {"created_at": last_record_date_0}
        assert actual_messages.state_messages[1].state.sourceStats.recordCount == 3.0
        assert actual_messages.state_messages[2].state.stream.stream_descriptor.name == "planets"
        assert actual_messages.state_messages[2].state.stream.stream_state == {"created_at": last_record_date_1}
        assert actual_messages.state_messages[2].state.sourceStats.recordCount == 2.0
        assert actual_messages.state_messages[3].state.stream.stream_descriptor.name == "dividers"
        assert actual_messages.state_messages[3].state.stream.stream_state == {"__ab_full_refresh_state_message": True}
        assert actual_messages.state_messages[3].state.sourceStats.recordCount == 4.0


def emits_successful_sync_status_messages(status_messages: List[AirbyteStreamStatus]) -> bool:
    return (len(status_messages) == 3 and status_messages[0] == AirbyteStreamStatus.STARTED
            and status_messages[1] == AirbyteStreamStatus.RUNNING and status_messages[2] == AirbyteStreamStatus.COMPLETE)


def validate_message_order(expected_message_order: List[Type], messages: List[AirbyteMessage]):
    if len(expected_message_order) != len(messages):
        pytest.fail(f"Expected message order count {len(expected_message_order)} did not match actual messages {len(messages)}")

    for i, message in enumerate(messages):
        if message.type != expected_message_order[i]:
            pytest.fail(f"At index {i} actual message type {message.type.name} did not match expected message type {expected_message_order[i].name}")
