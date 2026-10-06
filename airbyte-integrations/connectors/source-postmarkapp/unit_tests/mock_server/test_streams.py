# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
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
_POSTMARK_LIMIT_MESSAGE = (
    "Postmark returned more than 10,000 records for a single time window, which exceeds its API limit "
    "(ErrorCode 700). Lower the Slice Window (Minutes) setting and retry the sync."
)


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


def _stream_request(stream_name, fromdate, todate, offset=0):
    endpoint = PostmarkRequestBuilder.bounces_endpoint() if stream_name == _BOUNCES else PostmarkRequestBuilder.messages_endpoint()
    return endpoint.with_interval(fromdate, todate).with_pagination(offset=offset).build()


def _message_request(fromdate, todate, offset=0):
    return _stream_request(_MESSAGES, fromdate, todate, offset)


def _eastern_wall_time(value):
    return value.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S")


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
    def test_messages_and_bounces_use_hourly_est_windows(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T00:00:00Z").with_slice_window_minutes(60).build()
        expected_windows = [
            ("2025-01-01T19:00:00", "2025-01-01T20:00:00"),
            ("2025-01-01T20:00:00", "2025-01-01T21:00:01"),
        ]
        requests = []
        for stream_name, response_key in ((_MESSAGES, "Messages"), (_BOUNCES, "Bounces")):
            stream_requests = []
            for fromdate, todate in expected_windows:
                request = _stream_request(stream_name, fromdate, todate)
                http_mocker.get(request, _page(response_key, [], total_count=0))
                stream_requests.append(request)
            requests.append(stream_requests)

        with freezegun.freeze_time("2025-01-02T02:05:00Z"):
            for stream_name in (_MESSAGES, _BOUNCES):
                output = _read_stream(stream_name, SyncMode.incremental, config)
                assert output.errors == []
                assert output.records == []

        for stream_requests in requests:
            for request in stream_requests:
                http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_messages_and_bounces_use_hourly_edt_windows(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-08-02T00:00:00Z").with_slice_window_minutes(60).build()
        expected_windows = [
            ("2025-08-01T20:00:00", "2025-08-01T21:00:00"),
            ("2025-08-01T21:00:00", "2025-08-01T22:00:01"),
        ]
        requests = []
        for stream_name, response_key in ((_MESSAGES, "Messages"), (_BOUNCES, "Bounces")):
            stream_requests = []
            for fromdate, todate in expected_windows:
                request = _stream_request(stream_name, fromdate, todate)
                http_mocker.get(request, _page(response_key, [], total_count=0))
                stream_requests.append(request)
            requests.append(stream_requests)

        with freezegun.freeze_time("2025-08-02T02:05:00Z"):
            for stream_name in (_MESSAGES, _BOUNCES):
                output = _read_stream(stream_name, SyncMode.incremental, config)
                assert output.errors == []
                assert output.records == []

        for stream_requests in requests:
            for request in stream_requests:
                http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_hourly_windows_cover_the_ambiguous_hour_at_dst_fall_back(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-11-02T04:00:00Z").with_slice_window_minutes(60).build()
        before_fall_back = _message_request("2025-11-02T00:00:00", "2025-11-02T01:00:00")
        # 05:00-06:00Z (EDT) and 06:00-07:00Z (EST) are both 01:00-02:00 Eastern; the last window ends at now - 5m (07:00Z).
        ambiguous_hour_edt = _message_request("2025-11-02T01:00:00", "2025-11-02T02:00:00")
        ambiguous_hour_est = _message_request("2025-11-02T01:00:00", "2025-11-02T02:00:01")
        edt_record = {"MessageID": "edt", "ReceivedAt": "2025-11-02T01:30:00.0000000-04:00"}
        est_record = {"MessageID": "est", "ReceivedAt": "2025-11-02T01:30:00.0000000-05:00"}
        http_mocker.get(before_fall_back, _page("Messages", [], total_count=0))
        http_mocker.get(ambiguous_hour_edt, _page("Messages", [edt_record, est_record], total_count=2))
        http_mocker.get(ambiguous_hour_est, _page("Messages", [edt_record, est_record], total_count=2))

        with freezegun.freeze_time("2025-11-02T07:05:00Z"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        assert sorted(record.record.data["MessageID"] for record in output.records) == ["edt", "est"]
        http_mocker.assert_number_of_calls(before_fall_back, 1)
        http_mocker.assert_number_of_calls(ambiguous_hour_edt, 1)
        http_mocker.assert_number_of_calls(ambiguous_hour_est, 1)

    @HttpMocker()
    def test_record_on_window_boundary_is_emitted_once(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T00:00:00Z").with_slice_window_minutes(60).build()
        first_window = _message_request("2025-01-01T19:00:00", "2025-01-01T20:00:00")
        second_window = _message_request("2025-01-01T20:00:00", "2025-01-01T21:00:01")
        last_second = {"MessageID": "last-second", "ReceivedAt": "2025-01-01T19:59:59.5000000-05:00"}
        boundary = {"MessageID": "boundary", "ReceivedAt": "2025-01-01T20:00:00.0000000-05:00"}
        http_mocker.get(first_window, _page("Messages", [boundary, last_second], total_count=2))
        http_mocker.get(second_window, _page("Messages", [boundary], total_count=1))

        with freezegun.freeze_time("2025-01-02T02:05:00Z"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        assert sorted(record.record.data["MessageID"] for record in output.records) == ["boundary", "last-second"]
        http_mocker.assert_number_of_calls(first_window, 1)
        http_mocker.assert_number_of_calls(second_window, 1)

    @HttpMocker()
    def test_messages_incremental_resumes_from_state_written_with_record_offset(self, http_mocker):
        config = ConfigBuilder().build()
        request = _message_request("2025-01-02T06:30:00", "2025-01-02T06:55:01")
        http_mocker.get(request, _page("Messages", [], total_count=0))
        # The connector checkpoints ReceivedAt in Postmark's own offset, e.g. -0500 rather than +0000.
        state = StateBuilder().with_stream_state(_MESSAGES, {"ReceivedAt": "2025-01-02T06:30:00-0500"}).build()

        output = _read_stream(_MESSAGES, SyncMode.incremental, config, state)

        assert output.errors == []
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_messages_use_default_daily_windows(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-01T00:00:00Z").build()
        expected_windows = [
            ("2024-12-31T19:00:00", "2025-01-01T19:00:00"),
            ("2025-01-01T19:00:00", "2025-01-02T06:55:01"),
        ]
        requests = []
        for fromdate, todate in expected_windows:
            request = _message_request(fromdate, todate)
            http_mocker.get(request, _page("Messages", [], total_count=0))
            requests.append(request)

        output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        assert output.records == []
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_slice_window_minutes_configures_thirty_minute_windows(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T00:00:00Z").with_slice_window_minutes(30).build()
        expected_windows = [
            ("2025-01-01T19:00:00", "2025-01-01T19:30:00"),
            ("2025-01-01T19:30:00", "2025-01-01T20:00:01"),
        ]
        requests = []
        for fromdate, todate in expected_windows:
            request = _message_request(fromdate, todate)
            http_mocker.get(request, _page("Messages", [], total_count=0))
            requests.append(request)

        with freezegun.freeze_time("2025-01-02T01:05:00Z"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        assert output.records == []
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_messages_incremental_starts_at_state_without_lookback(self, http_mocker):
        config = ConfigBuilder().build()
        request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01")
        http_mocker.get(
            request,
            _page("Messages", _messages("incremental", 1, "2025-01-02T06:30:00.8782715-05:00"), total_count=1),
        )
        state = StateBuilder().with_stream_state(_MESSAGES, {"ReceivedAt": "2025-01-02T11:00:00+0000"}).build()

        output = _read_stream(_MESSAGES, SyncMode.incremental, config, state)

        assert output.errors == []
        assert len(output.records) == 1
        state_value = output.most_recent_state.stream_state.__dict__["ReceivedAt"]
        assert state_value == "2025-01-02T06:30:00-0500"
        datetime.strptime(state_value, "%Y-%m-%dT%H:%M:%S%z")
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_bounces_default_start_date_and_seven_digit_cursor_state(self, http_mocker):
        end = datetime.fromisoformat(_FROZEN_NOW.replace("Z", "+00:00")) - timedelta(minutes=5)
        first_start = datetime.fromisoformat(_FROZEN_NOW.replace("Z", "+00:00")) - timedelta(days=365)
        record_datetime = datetime.fromisoformat("2024-12-01T16:09:19.6421112-05:00")
        record = {"ID": 1, "BouncedAt": "2024-12-01T16:09:19.6421112-05:00"}
        start = first_start
        first_request = None
        while start < end:
            next_start = start + timedelta(days=1)
            slice_end = min(next_start - timedelta(seconds=1), end)
            fromdate = _eastern_wall_time(start)
            todate = _eastern_wall_time(slice_end + timedelta(seconds=1))
            request = _stream_request(_BOUNCES, fromdate, todate)
            if first_request is None:
                first_request = request
            records = [record] if start <= record_datetime <= slice_end else []
            http_mocker.get(request, _page("Bounces", records, total_count=len(records)))
            start = next_start

        config = ConfigBuilder().build()
        output = _read_stream(_BOUNCES, SyncMode.incremental, config)

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data["BouncedAt"] == record["BouncedAt"]
        state_value = output.most_recent_state.stream_state.__dict__["BouncedAt"]
        assert state_value == "2024-12-01T16:09:19-0500"
        datetime.strptime(state_value, "%Y-%m-%dT%H:%M:%S%z")
        assert first_request is not None
        expected_first_request = _stream_request(_BOUNCES, "2024-01-03T07:00:00", "2024-01-04T07:00:00")
        assert first_request == expected_first_request
        http_mocker.assert_number_of_calls(first_request, 1)

    @HttpMocker()
    def test_error_code_700_fails_fast_with_config_error(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01")
        response = HttpResponse(
            body=json.dumps({"ErrorCode": 700, "Message": "The combination of count and offset is too large."}),
            status_code=422,
        )
        http_mocker.get(request, response)

        with patch("time.sleep"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert any(
            error.trace.error.failure_type == FailureType.config_error and error.trace.error.message == _POSTMARK_LIMIT_MESSAGE
            for error in output.errors
        )
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_other_422_responses_fail_without_retry(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01")
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"ErrorCode": 701, "Message": "Invalid date filter."}), status_code=422),
        )

        output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert any(error.trace.error.message == "Postmark rejected the request: Invalid date filter." for error in output.errors)
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_rate_limited_messages_request_retries_then_reads_record(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01")
        http_mocker.get(
            request,
            [
                HttpResponse(body=json.dumps({"Message": "Rate limit exceeded."}), status_code=429),
                HttpResponse(body=json.dumps({"Message": "Rate limit exceeded."}), status_code=429),
                _page("Messages", _messages("retried", 1, "2025-01-02T06:30:00.1234567-05:00"), total_count=1),
            ],
        )

        with patch("time.sleep"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        assert len(output.records) == 1
        assert output.records[0].record.data["MessageID"] == "retried-0"
        http_mocker.assert_number_of_calls(request, 3)

    @HttpMocker()
    def test_messages_stops_after_empty_second_page(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        first_request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01")
        second_request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01", offset=500)
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
