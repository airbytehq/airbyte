# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import NylasRequestBuilder
from mock_server.response_builder import NylasResponseBuilder


@pytest.mark.parametrize("event_ids", [["event-1", "event-2"], []])
def test_events_skips_calendar_not_found(event_ids):
    with HttpMocker() as http_mocker:
        assert_calendar_not_found_is_skipped(http_mocker, event_ids)


def events_request(calendar_id):
    return (
        NylasRequestBuilder("grants/grant-1/events")
        .with_query_param("calendar_id", calendar_id)
        .with_query_param("start", "1704067200")
        .with_query_param("end", "1704153600")
        .build()
    )


def mock_parents(http_mocker):
    http_mocker.get(NylasRequestBuilder("grants").build(), NylasResponseBuilder.records([{"id": "grant-1"}]))
    http_mocker.get(
        NylasRequestBuilder("grants/grant-1/calendars").build(),
        NylasResponseBuilder.records([{"id": "public-holidays"}, {"id": "primary"}]),
    )


def read_events():
    config = ConfigBuilder().build()
    return read(
        get_source(config),
        config=config,
        catalog=CatalogBuilder().with_stream("events", SyncMode.incremental).build(),
    )


def assert_calendar_not_found_is_skipped(http_mocker, event_ids):
    mock_parents(http_mocker)
    missing_calendar_request = events_request("public-holidays")
    primary_calendar_request = events_request("primary")
    http_mocker.get(missing_calendar_request, NylasResponseBuilder.error(404, "Not Found"))
    http_mocker.get(
        primary_calendar_request,
        NylasResponseBuilder.records([{"id": event_id, "calendar_id": "primary", "updated_at": 1704070800} for event_id in event_ids]),
    )
    output = read_events()

    assert [record.record.data["id"] for record in output.records] == event_ids
    assert not output.errors
    assert not any(log.log.level == "ERROR" for log in output.logs)
    assert AirbyteStreamStatus.INCOMPLETE not in output.get_stream_statuses("events")
    assert any(
        log.log.message == "Skipping events for the requested calendar_id: 404 Not Found. This calendar may not support event listing."
        for log in output.logs
    )
    http_mocker.assert_number_of_calls(missing_calendar_request, 1)
    http_mocker.assert_number_of_calls(primary_calendar_request, 1)


def test_events_unauthorized_still_fails():
    with HttpMocker() as http_mocker:
        mock_parents(http_mocker)
        unauthorized_request = events_request("public-holidays")
        http_mocker.get(unauthorized_request, NylasResponseBuilder.error(401, "Unauthorized"))
        http_mocker.get(events_request("primary"), NylasResponseBuilder.records([]))

        output = read_events()

        assert not output.records
        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        assert "Unauthorized" in output.errors[0].trace.error.message
        assert AirbyteStreamStatus.INCOMPLETE in output.get_stream_statuses("events")
        http_mocker.assert_number_of_calls(unauthorized_request, 1)
