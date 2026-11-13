# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.models.outcome import ExpectedOutcome

from .zoom_mocks import (
    assert_completed_without_errors,
    assert_failed_with_config_error,
    json_response,
    mock_token,
    read_stream,
    records_data,
    request,
    zoom_error,
)


_STREAM = "zoom_events"
_STATUSES = ("upcoming", "past", "draft", "cancelled")


def _events_request(status: str, next_page_token: str = ""):
    params = {"role_type": "host", "event_status_type": status, "page_size": "300"}
    if next_page_token:
        params["next_page_token"] = next_page_token
    return request("/zoom_events/events", params)


@freezegun.freeze_time("2026-10-20T12:00:00Z")
class TestZoomEvents(TestCase):
    @HttpMocker()
    def test_lists_all_statuses_and_paginates(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        first_requests = [_events_request(status) for status in _STATUSES]
        second_page = _events_request("upcoming", "event-page-2")
        http_mocker.get(
            first_requests[0],
            json_response({"events": [{"event_id": "event-1", "name": "Conference"}], "next_page_token": "event-page-2"}),
        )
        http_mocker.get(second_page, json_response({"events": [{"event_id": "event-2", "name": "Summit"}]}))
        for status, current in zip(_STATUSES[1:], first_requests[1:]):
            http_mocker.get(current, json_response({"events": [{"event_id": status}]}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert {record["event_id"] for record in records_data(output)} == {
            "event-1",
            "event-2",
            "past",
            "draft",
            "cancelled",
        }
        for current in first_requests:
            http_mocker.assert_number_of_calls(current, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_empty_response_still_requests_each_status_once(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        requests = [_events_request(status) for status in _STATUSES]
        for current in requests:
            http_mocker.get(current, json_response({"events": [], "total_records": 0}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert output.records == []
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_missing_scope_is_configuration_error(self, http_mocker: HttpMocker):
        mock_token(http_mocker)
        requests = [_events_request(status) for status in _STATUSES]
        for status, current in zip(_STATUSES, requests):
            if status == "upcoming":
                http_mocker.get(current, zoom_error(4711, "Missing Zoom Events scope.", status_code=400))
            else:
                http_mocker.get(current, json_response({"events": [], "total_records": 0}))

        output = read_stream(_STREAM, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        assert_failed_with_config_error(output, _STREAM)
        assert output.is_in_logs("zoom_events_basic:read:admin")
        assert output.is_in_logs("zoom_events:read:list_events:admin")
        for current in requests:
            http_mocker.assert_number_of_calls(current, 1)
