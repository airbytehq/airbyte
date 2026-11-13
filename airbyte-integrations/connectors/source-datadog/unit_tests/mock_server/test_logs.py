# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import datetime
from typing import Any
from unittest import TestCase

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import now_is, read_stream, saved_state, state_of, stream_errors
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.request_builder import DatadogRequestBuilder
from unit_tests.mock_server.response_builder import UNEXPECTED_ERROR_BODIES, DatadogPaginatedResponseBuilder, datadog_error


_CONFIG = ConfigBuilder().with_start_date("2026-10-05T00:00:00Z").with_end_date("2026-10-06T00:00:00Z").build()


def _request(start: str = "2026-10-05T00:00:00.000000Z", end: str = "2026-10-06T00:00:00.000000Z") -> DatadogRequestBuilder:
    return (
        DatadogRequestBuilder.logs_endpoint()
        .with_query_param("filter[from]", start)
        .with_query_param("filter[to]", end)
        .with_query_param("page[limit]", 5000)
    )


def _log(log_id: str, timestamp: str = "2026-10-05T10:00:00.000Z") -> dict[str, Any]:
    return {"id": log_id, "attributes": {"timestamp": timestamp}}


def _page(*logs: dict[str, Any]) -> HttpResponse:
    return DatadogPaginatedResponseBuilder("data").with_records(list(logs)).build()


class TestLogsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _request().build(),
            DatadogPaginatedResponseBuilder("data")
            .with_records([_log("log-1"), _log("log-2")])
            .with_meta({"page": {"after": "next-page"}})
            .build(),
        )
        http_mocker.get(_request().with_query_param("page[cursor]", "next-page").build(), _page(_log("log-3")))

        output = read_stream("logs", config=_CONFIG)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["log-1", "log-2", "log-3"]

    @HttpMocker()
    def test_ends_on_a_null_meta_and_on_a_null_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(
            request,
            [
                DatadogPaginatedResponseBuilder("data").with_records([_log("log-1")]).with_meta(None).build(),
                DatadogPaginatedResponseBuilder("data").with_records([_log("log-2")]).with_meta({"page": None}).build(),
            ],
        )

        null_meta = read_stream("logs", config=_CONFIG)
        null_page = read_stream("logs", config=_CONFIG)

        assert null_meta.errors == []
        assert null_page.errors == []
        assert [message.record.data["id"] for message in null_meta.records + null_page.records] == ["log-1", "log-2"]
        http_mocker.assert_number_of_calls(request, 2)

    @HttpMocker()
    def test_ends_on_an_empty_page(self, http_mocker: HttpMocker) -> None:
        request = _request().build()
        http_mocker.get(request, DatadogPaginatedResponseBuilder("data").with_meta({"page": {"after": "next-page"}}).build())

        output = read_stream("logs", config=_CONFIG)

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_fails_on_a_query_that_datadog_rejects(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), datadog_error(400, ["Invalid query", "unexpected token"]))

        output = read_stream("logs", config=_CONFIG, expecting_error=True)

        errors = stream_errors(output, "logs")
        assert [(error.failure_type, error.message) for error in errors] == [
            (
                FailureType.config_error,
                "Datadog rejected the log search query: Invalid query, unexpected token. Check the Query field.",
            )
        ]

    @HttpMocker()
    def test_first_sync_saves_the_time_of_the_newest_log(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request().build(), _page(_log("log-2", "2026-10-05T11:30:00.456Z"), _log("log-1", "2026-10-05T10:00:00.123Z")))

        output = read_stream("logs", SyncMode.incremental, config=_CONFIG)

        assert output.errors == []
        assert [message.record.data["sync_date"] for message in output.records] == ["2026-10-05T11:30:00.456Z", "2026-10-05T10:00:00.123Z"]
        assert saved_state(output) == {"sync_date": "2026-10-05T11:30:00.456000Z"}

    @HttpMocker()
    def test_second_sync_asks_from_one_day_before_the_saved_state(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_start_date("2026-10-01T00:00:00Z").with_end_date("2026-10-06T00:00:00Z").build()
        http_mocker.get(_request(start="2026-10-01T00:00:00.000000Z").build(), _page(_log("log-1", "2026-10-05T11:30:00.456Z")))
        http_mocker.get(
            _request(start="2026-10-04T11:30:00.456000Z").build(),
            _page(_log("log-2", "2026-10-05T15:00:00.789Z"), _log("log-1", "2026-10-05T11:30:00.456Z")),
        )

        first = read_stream("logs", SyncMode.incremental, config=config)
        second = read_stream("logs", SyncMode.incremental, config=config, state=state_of("logs", saved_state(first)))

        assert first.errors == []
        assert saved_state(first) == {"sync_date": "2026-10-05T11:30:00.456000Z"}
        assert second.errors == []
        assert [message.record.data["id"] for message in second.records] == ["log-2", "log-1"]
        assert saved_state(second) == {"sync_date": "2026-10-05T15:00:00.789000Z"}

    @HttpMocker()
    def test_reads_a_state_in_the_old_format(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_start_date("2026-09-15T00:00:00Z").with_end_date("2026-10-06T00:00:00Z").build()
        http_mocker.get(_request(start="2026-09-30T00:00:00.000000Z").build(), _page(_log("log-1", "2026-10-05T10:00:00.123Z")))

        output = read_stream("logs", SyncMode.incremental, config=config, state=state_of("logs", {"sync_date": "2026-10-01T00:00:00Z"}))

        assert output.errors == []
        assert saved_state(output) == {"sync_date": "2026-10-05T10:00:00.123000Z"}

    @HttpMocker()
    def test_monthly_windows_leave_no_gap(self, http_mocker: HttpMocker) -> None:
        # Datadog reads `filter[to]` as exclusive, so a window that ended at 23:59:59 would lose its last second.
        config = ConfigBuilder().with_start_date("2026-10-01T00:00:00Z").with_end_date("2026-11-12T22:00:00Z").build()
        http_mocker.get(
            _request(start="2026-10-01T00:00:00.000000Z", end="2026-10-31T23:59:59.999999Z").build(),
            _page(_log("log-1", "2026-10-31T23:59:59.999Z")),
        )
        http_mocker.get(
            _request(start="2026-11-01T00:00:00.000000Z", end="2026-11-12T22:00:00.000000Z").build(),
            _page(_log("log-2", "2026-11-12T21:01:40.305Z")),
        )

        output = read_stream("logs", SyncMode.incremental, config=config)

        assert output.errors == []
        assert sorted(message.record.data["id"] for message in output.records) == ["log-1", "log-2"]
        assert saved_state(output) == {"sync_date": "2026-11-12T21:01:40.305000Z"}

    @HttpMocker()
    def test_with_no_end_date_the_window_ends_at_the_time_of_the_sync(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_start_date("2026-11-01T00:00:00Z").build()
        request = _request(start="2026-11-01T00:00:00.000000Z", end="2026-11-13T10:00:05.000000Z").build()
        http_mocker.get(request, _page())

        with now_is(datetime.datetime(2026, 11, 13, 10, 0, 5, 250000, tzinfo=datetime.timezone.utc)):
            output = read_stream("logs", SyncMode.incremental, config=config)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("body", UNEXPECTED_ERROR_BODIES.values(), ids=UNEXPECTED_ERROR_BODIES.keys())
def test_rejected_query_message_survives_an_unexpected_body(body: str) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request().build(), HttpResponse(body, 400))

        output = read_stream("logs", config=_CONFIG, expecting_error=True)

    assert [error.message for error in stream_errors(output, "logs")] == ["Datadog rejected the log search query. Check the Query field."]
