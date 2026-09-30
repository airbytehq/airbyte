# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import PostmarkRequestBuilder


_FROZEN_NOW = "2025-01-02T12:00:00Z"
_MESSAGES = "messages"
_BOUNCES = "bounces"
_SERVERS = "servers"


def _read_stream(stream_name, sync_mode, config, state=None) -> EntrypointOutput:
    state = state or StateBuilder().build()
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    source = get_source(config=config, state=state)
    return read(source, config=config, catalog=catalog, state=state)


def _page(key, records, total_count=None) -> HttpResponse:
    body = {key: records}
    if total_count is not None:
        body["TotalCount"] = total_count
    return HttpResponse(body=json.dumps(body))


def _messages(prefix, count, received_at):
    return [{"MessageID": f"{prefix}-{index}", "ReceivedAt": received_at} for index in range(count)]


def _message_request(fromdate, todate, offset=0):
    return PostmarkRequestBuilder.messages_endpoint().with_interval(fromdate, todate).with_pagination(offset=offset).build()


@freezegun.freeze_time(_FROZEN_NOW)
class TestPostmarkStreams(TestCase):
    @HttpMocker()
    def test_servers_paginates_with_count_and_account_accept_header(self, http_mocker):
        first_request = PostmarkRequestBuilder.servers_endpoint().with_pagination().build()
        second_request = PostmarkRequestBuilder.servers_endpoint().with_pagination(offset=500).build()
        first_records = [{"ID": index} for index in range(500)]
        second_records = [{"ID": index} for index in range(500, 503)]
        http_mocker.get(first_request, _page("Servers", first_records))
        http_mocker.get(second_request, _page("Servers", second_records))

        output = _read_stream(_SERVERS, SyncMode.full_refresh, ConfigBuilder().build())

        assert output.errors == []
        assert len(output.records) == 503
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    @HttpMocker()
    def test_messages_full_refresh_slices_and_paginates_with_exact_filters(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-01T00:00:00Z").build()
        first_start = "2024-12-31T19:00:00"
        first_end = "2025-01-01T19:00:00"
        second_start = "2025-01-01T19:00:00"
        second_end = "2025-01-02T07:00:01"
        first_request = _message_request(first_start, first_end)
        second_request = _message_request(first_start, first_end, offset=500)
        third_request = _message_request(second_start, second_end)
        http_mocker.get(
            first_request,
            _page("Messages", _messages("slice1", 500, "2025-01-01T10:00:00.1234567-05:00"), total_count=510),
        )
        http_mocker.get(
            second_request,
            _page("Messages", _messages("slice1-more", 10, "2025-01-01T10:30:00.1234567-05:00"), total_count=510),
        )
        http_mocker.get(
            third_request,
            _page("Messages", _messages("slice2", 1, "2025-01-02T06:00:00.1234567-05:00"), total_count=1),
        )

        output = _read_stream(_MESSAGES, SyncMode.full_refresh, config)

        assert output.errors == []
        assert len(output.records) == 511
        assert all(".1234567-05:00" in message.record.data["ReceivedAt"] for message in output.records)
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)
        http_mocker.assert_number_of_calls(third_request, 1)

    @HttpMocker()
    def test_messages_incremental_uses_state_lookback_and_parses_seven_digit_fraction(self, http_mocker):
        config = ConfigBuilder().build()
        request = _message_request("2025-01-02T00:00:00", "2025-01-02T07:00:01")
        http_mocker.get(
            request,
            _page("Messages", _messages("incremental", 1, "2025-01-02T06:30:00.8782715-05:00"), total_count=1),
        )
        state = StateBuilder().with_stream_state(_MESSAGES, {"ReceivedAt": "2025-01-02T06:00:00+0000"}).build()

        output = _read_stream(_MESSAGES, SyncMode.incremental, config, state)

        assert output.errors == []
        assert len(output.records) == 1
        state_value = output.most_recent_state.stream_state.__dict__["ReceivedAt"]
        assert state_value == "2025-01-02T06:30:00-0500"
        datetime.strptime(state_value, "%Y-%m-%dT%H:%M:%S%z")
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_bounces_default_start_date_and_seven_digit_cursor_state(self, http_mocker):
        end = datetime.fromisoformat(_FROZEN_NOW.replace("Z", "+00:00"))
        first_start = end - timedelta(days=365)
        record_datetime = datetime.fromisoformat("2024-12-01T16:09:19.6421112-05:00")
        record = {
            "ID": 1,
            "BouncedAt": "2024-12-01T16:09:19.6421112-05:00",
        }
        start = first_start
        first_request = None
        while start < end:
            next_start = start + timedelta(days=1)
            slice_end = end if next_start >= end else next_start - timedelta(seconds=1)
            fromdate = (start - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S")
            todate = (slice_end + timedelta(seconds=1) - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S")
            request = PostmarkRequestBuilder.bounces_endpoint().with_interval(fromdate, todate).with_pagination().build()
            if first_request is None:
                first_request = request
            records = [record] if start <= record_datetime <= slice_end else []
            http_mocker.get(request, _page("Bounces", records, total_count=len(records)))
            start = next_start

        output = _read_stream(_BOUNCES, SyncMode.incremental, ConfigBuilder().build())

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data["BouncedAt"] == record["BouncedAt"]
        state_value = output.most_recent_state.stream_state.__dict__["BouncedAt"]
        assert state_value == "2024-12-01T16:09:19-0500"
        datetime.strptime(state_value, "%Y-%m-%dT%H:%M:%S%z")
        assert first_request is not None
        expected_first_request = (
            PostmarkRequestBuilder.bounces_endpoint().with_interval("2024-01-03T07:00:00", "2024-01-04T07:00:00").with_pagination().build()
        )
        assert first_request == expected_first_request
        http_mocker.assert_number_of_calls(first_request, 1)

    @HttpMocker()
    def test_messages_stops_after_empty_second_page(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T00:00:00Z").build()
        first_request = _message_request("2025-01-01T19:00:00", "2025-01-02T07:00:01")
        second_request = _message_request("2025-01-01T19:00:00", "2025-01-02T07:00:01", offset=500)
        http_mocker.get(
            first_request,
            _page("Messages", _messages("termination", 500, "2025-01-02T06:00:00.1234567-05:00"), total_count=500),
        )
        http_mocker.get(second_request, _page("Messages", [], total_count=500))

        output = _read_stream(_MESSAGES, SyncMode.full_refresh, config)

        assert output.errors == []
        assert len(output.records) == 500
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)
