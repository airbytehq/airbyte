# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from typing import Any
from unittest import TestCase

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import CONFIG, get_source, read_stream, saved_state, state_of, stream_errors
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import DatadogPaginatedResponseBuilder, datadog_error


_STREAM = "events"
_CONFIG = ConfigBuilder().with_start_date("2026-10-05T00:00:00Z").with_end_date("2026-10-06T00:00:00Z").build()


# A window sends the start of the next window as `filter[to]`: its own end plus one microsecond.
def _request(start: str = "2026-10-05T00:00:00.000000Z", end: str = "2026-10-06T00:00:00.000001Z") -> DatadogRequestBuilder:
    return (
        DatadogRequestBuilder("v2/events")
        .with_query_param("filter[from]", start)
        .with_query_param("filter[to]", end)
        .with_query_param("page[limit]", 1000)
    )


def _event(event_id: str, timestamp: str = "2026-10-05T10:00:00.000Z") -> dict[str, Any]:
    return {"id": event_id, "type": "event", "attributes": {"timestamp": timestamp}}


def _page(*events: dict[str, Any]) -> HttpResponse:
    return DatadogPaginatedResponseBuilder("data").with_records(list(events)).build()


class TestEventsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data")
            .with_records([_event("event-1"), _event("event-2")])
            .with_meta({"page": {"after": "next-page"}})
            .build(),
        )
        http_mocker.get(_request().with_query_param("page[cursor]", "next-page").build(), _page(_event("event-3")))

        output = read_stream(_STREAM, config=_CONFIG)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event-1", "event-2", "event-3"]

    @HttpMocker()
    def test_ends_on_a_null_meta_and_on_a_null_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(
            request,
            [
                DatadogPaginatedResponseBuilder("data").with_records([_event("event-1")]).with_meta(None).build(),
                DatadogPaginatedResponseBuilder("data").with_records([_event("event-2")]).with_meta({"page": None}).build(),
            ],
        )

        null_meta = read_stream(_STREAM, config=_CONFIG)
        null_page = read_stream(_STREAM, config=_CONFIG)

        assert null_meta.errors == []
        assert null_page.errors == []
        assert [message.record.data["id"] for message in null_meta.records + null_page.records] == ["event-1", "event-2"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_ends_on_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_meta({"page": {"after": "next-page"}}).build())

        output = read_stream(_STREAM, config=_CONFIG)

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_copies_the_timestamp_into_sync_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), _page(_event("event-1", "2026-10-05T10:00:00.123Z")))

        output = read_stream(_STREAM, config=_CONFIG)

        assert output.errors == []
        assert [message.record.data["sync_date"] for message in output.records] == ["2026-10-05T10:00:00.123Z"]

    @HttpMocker()
    def test_does_not_send_the_log_search_query(self, http_mocker: HttpMocker) -> None:
        # The Query field holds a log search. Event Management has a search syntax of its own.
        config = (
            ConfigBuilder().with_start_date("2026-10-05T00:00:00Z").with_end_date("2026-10-06T00:00:00Z").with_query("service:web").build()
        )
        http_mocker.get(_request().build(), _page(_event("event-1")))

        output = read_stream(_STREAM, config=config)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event-1"]

    @HttpMocker()
    def test_missing_permission_names_events_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(403, ["Forbidden", "Failed permission authorization checks"]))

        output = read_stream(_STREAM, config=_CONFIG, expecting_error=True)

        errors = stream_errors(output, _STREAM)
        assert errors
        assert {(error.failure_type, error.message) for error in errors} == {
            (
                FailureType.config_error,
                "The Application Key lacks the events_read permission: Forbidden, Failed permission authorization checks. "
                "Grant events_read to the Application Key in Datadog.",
            )
        }

    @HttpMocker()
    def test_first_sync_saves_the_time_of_the_newest_event(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().build(), _page(_event("event-2", "2026-10-05T11:30:00.456Z"), _event("event-1", "2026-10-05T10:00:00.123Z"))
        )

        output = read_stream(_STREAM, SyncMode.incremental, config=_CONFIG)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["event-2", "event-1"]
        assert saved_state(output) == {"sync_date": "2026-10-05T11:30:00.456000Z"}

    @HttpMocker()
    def test_saves_a_timestamp_without_fractional_seconds(self, http_mocker: HttpMocker) -> None:
        # Datadog's own recorded answers carry event timestamps such as `2022-06-20T17:07:32Z`.
        http_mocker.get(_request().build(), _page(_event("event-1", "2026-10-05T11:30:00Z")))

        output = read_stream(_STREAM, SyncMode.incremental, config=_CONFIG)

        assert output.errors == []
        assert saved_state(output) == {"sync_date": "2026-10-05T11:30:00.000000Z"}

    @HttpMocker()
    def test_second_sync_asks_from_one_day_before_the_saved_state(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_start_date("2026-10-01T00:00:00Z").with_end_date("2026-10-06T00:00:00Z").build()
        http_mocker.get(_request(start="2026-10-01T00:00:00.000000Z").build(), _page(_event("event-1", "2026-10-05T11:30:00.456Z")))
        http_mocker.get(
            _request(start="2026-10-04T11:30:00.456000Z").build(),
            _page(_event("event-2", "2026-10-05T15:00:00.789Z"), _event("event-1", "2026-10-05T11:30:00.456Z")),
        )

        first = read_stream(_STREAM, SyncMode.incremental, config=config)
        second = read_stream(_STREAM, SyncMode.incremental, config=config, state=state_of(_STREAM, saved_state(first)))

        assert first.errors == []
        assert saved_state(first) == {"sync_date": "2026-10-05T11:30:00.456000Z"}
        assert second.errors == []
        assert [message.record.data["id"] for message in second.records] == ["event-2", "event-1"]
        assert saved_state(second) == {"sync_date": "2026-10-05T15:00:00.789000Z"}

    @HttpMocker()
    def test_monthly_windows_leave_no_gap(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_start_date("2026-10-01T00:00:00Z").with_end_date("2026-11-12T22:00:00Z").build()
        http_mocker.get(
            _request(start="2026-10-01T00:00:00.000000Z", end="2026-11-01T00:00:00.000000Z").build(),
            _page(_event("event-1", "2026-10-31T23:59:59.999Z")),
        )
        http_mocker.get(
            _request(start="2026-11-01T00:00:00.000000Z", end="2026-11-12T22:00:00.000001Z").build(),
            _page(_event("event-2", "2026-11-12T21:01:40.305Z")),
        )

        output = read_stream(_STREAM, SyncMode.incremental, config=config)

        assert output.errors == []
        assert sorted(message.record.data["id"] for message in output.records) == ["event-1", "event-2"]
        assert saved_state(output) == {"sync_date": "2026-11-12T21:01:40.305000Z"}


def test_primary_key_is_the_event_id() -> None:
    catalog = get_source().discover(logging.getLogger("airbyte"), CONFIG)

    assert [stream.source_defined_primary_key for stream in catalog.streams if stream.name == _STREAM] == [[["id"]]]
