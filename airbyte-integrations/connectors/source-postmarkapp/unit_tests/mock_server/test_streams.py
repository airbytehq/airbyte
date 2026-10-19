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
_LOWER_WINDOW_GUIDANCE = "Lower the Slice Window (Minutes) setting so that each window has fewer than 10,000 records."


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


def _assert_config_error(output, message):
    # The CDK also emits a "did not sync successfully" trace for the stream, carrying the same failure type.
    assert output.errors
    assert all(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
    assert message in [error.trace.error.message for error in output.errors]


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
        # 05:00-06:00Z (EDT) and 06:00-07:00Z (EST) are both 01:00-02:00 Eastern, which Postmark may read as either hour.
        # The EDT window asks for 00:59:59-02:00:00, covering it under both readings; the last window ends at now - 5m (07:00Z).
        ambiguous_hour_edt = _message_request("2025-11-02T00:59:59", "2025-11-02T02:00:00")
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
    def test_window_starting_off_the_hour_across_dst_fall_back_is_not_collapsed(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-11-01T00:00:00Z").with_slice_window_minutes(60).build()
        # Incremental windows start an hour before the last record's second, so they rarely start on the hour.
        state = StateBuilder().with_stream_state(_MESSAGES, {"ReceivedAt": "2025-11-02T06:17:23+0000"}).build()
        # 05:17:23-06:17:22Z would map to 01:17:23-01:17:23 Eastern with a single offset per boundary.
        crossing_window = _message_request("2025-11-02T00:59:59", "2025-11-02T02:00:00")
        last_window = _message_request("2025-11-02T01:17:23", "2025-11-02T02:17:24")
        edt_record = {"MessageID": "edt", "ReceivedAt": "2025-11-02T01:30:00.0000000-04:00"}
        est_record = {"MessageID": "est", "ReceivedAt": "2025-11-02T01:30:00.0000000-05:00"}
        http_mocker.get(crossing_window, _page("Messages", [edt_record, est_record], total_count=2))
        http_mocker.get(last_window, _page("Messages", [edt_record, est_record], total_count=2))

        with freezegun.freeze_time("2025-11-02T07:22:23Z"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config, state)

        assert output.errors == []
        assert sorted(record.record.data["MessageID"] for record in output.records) == ["edt", "est"]
        http_mocker.assert_number_of_calls(crossing_window, 1)
        http_mocker.assert_number_of_calls(last_window, 1)

    @HttpMocker()
    def test_hourly_windows_skip_the_missing_hour_at_dst_spring_forward(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-03-09T05:00:00Z").with_slice_window_minutes(60).build()
        # 02:00-03:00 Eastern does not exist on 2025-03-09; the window ending at 07:00Z must ask for 03:00, not 02:00.
        expected_windows = [
            ("2025-03-09T00:00:00", "2025-03-09T01:00:00"),
            ("2025-03-09T01:00:00", "2025-03-09T03:00:00"),
            ("2025-03-09T03:00:00", "2025-03-09T04:00:01"),
        ]
        requests = []
        for fromdate, todate in expected_windows:
            request = _message_request(fromdate, todate)
            http_mocker.get(request, _page("Messages", [], total_count=0))
            requests.append(request)

        with freezegun.freeze_time("2025-03-09T08:05:00Z"):
            output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

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
        # The state is 06:30 EST; the one-hour lookback starts the window at 05:30 EST.
        request = _message_request("2025-01-02T05:30:00", "2025-01-02T06:55:01")
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
    def test_messages_incremental_starts_one_hour_before_state(self, http_mocker):
        config = ConfigBuilder().build()
        # The state is 11:00Z (06:00 EST); re-reading the hour before it picks up records Postmark indexed late.
        request = _message_request("2025-01-02T05:00:00", "2025-01-02T06:55:01")
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
    def test_window_with_10000_or_more_records_fails_as_config_error_before_emitting(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        # With exactly 10,000 records the last page is full, so the paginator would still request offset 10,000 and get a 422.
        for stream_name, response_key, total_count in ((_MESSAGES, "Messages", 10000), (_BOUNCES, "Bounces", 12000)):
            window = _stream_request(stream_name, "2025-01-02T06:00:00", "2025-01-02T06:55:01")
            http_mocker.get(
                window, _page(response_key, _messages("oversized", 500, "2025-01-02T06:10:00.0000000-05:00"), total_count=total_count)
            )

            output = _read_stream(stream_name, SyncMode.incremental, config)

            assert output.records == []
            _assert_config_error(
                output,
                f"Postmark found {total_count} records in one 1440-minute window, but returns at most 10,000 per search. {_LOWER_WINDOW_GUIDANCE}",
            )
            http_mocker.assert_number_of_calls(window, 1)

    @HttpMocker()
    def test_window_with_9999_records_is_read_in_full(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        requests = []
        for page in range(20):
            records = _messages(f"page{page}", 500 if page < 19 else 499, "2025-01-02T06:10:00.0000000-05:00")
            request = _message_request("2025-01-02T06:00:00", "2025-01-02T06:55:01", offset=page * 500)
            http_mocker.get(request, _page("Messages", records, total_count=9999))
            requests.append(request)

        output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert output.errors == []
        assert len(output.records) == 9999
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_oversized_window_keeps_progress_from_earlier_windows(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").with_slice_window_minutes(30).build()
        first_window = _message_request("2025-01-02T06:00:00", "2025-01-02T06:30:00")
        oversized_window = _message_request("2025-01-02T06:30:00", "2025-01-02T06:55:01")
        http_mocker.get(first_window, _page("Messages", _messages("first", 1, "2025-01-02T06:10:00.0000000-05:00"), total_count=1))
        http_mocker.get(oversized_window, _page("Messages", [], total_count=15000))

        output = _read_stream(_MESSAGES, SyncMode.incremental, config)

        assert [record.record.data["MessageID"] for record in output.records] == ["first-0"]
        assert output.most_recent_state.stream_state.__dict__["ReceivedAt"] == "2025-01-02T06:10:00-0500"
        _assert_config_error(
            output, f"Postmark found 15000 records in one 30-minute window, but returns at most 10,000 per search. {_LOWER_WINDOW_GUIDANCE}"
        )
        http_mocker.assert_number_of_calls(first_window, 1)
        http_mocker.assert_number_of_calls(oversized_window, 1)

    @HttpMocker()
    def test_lowered_slice_window_resumes_from_state(self, http_mocker):
        # After an oversized-window failure the user lowers the setting; the next sync starts an hour before the saved state.
        config = ConfigBuilder().with_start_date("2025-01-02T00:00:00Z").with_slice_window_minutes(15).build()
        state = StateBuilder().with_stream_state(_MESSAGES, {"ReceivedAt": "2025-01-02T06:10:00-0500"}).build()
        expected_windows = [
            ("2025-01-02T05:10:00", "2025-01-02T05:25:00"),
            ("2025-01-02T05:25:00", "2025-01-02T05:40:00"),
            ("2025-01-02T05:40:00", "2025-01-02T05:55:00"),
            ("2025-01-02T05:55:00", "2025-01-02T06:10:00"),
            ("2025-01-02T06:10:00", "2025-01-02T06:25:00"),
            ("2025-01-02T06:25:00", "2025-01-02T06:40:00"),
            ("2025-01-02T06:40:00", "2025-01-02T06:55:01"),
        ]
        requests = []
        for fromdate, todate in expected_windows:
            request = _message_request(fromdate, todate)
            http_mocker.get(request, _page("Messages", [], total_count=0))
            requests.append(request)

        output = _read_stream(_MESSAGES, SyncMode.incremental, config, state)

        assert output.errors == []
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)

    def test_offset_limit_error_fails_as_config_error(self):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").with_slice_window_minutes(60).build()
        # The messages wording was seen live; the bounces wording isn't documented, so cover a message naming only the 10,000 limit.
        cases = (
            (_MESSAGES, {"ErrorCode": 700, "Message": "The combination of count and offset is too large."}),
            (_BOUNCES, {"ErrorCode": 1000, "Message": "Count + Offset cannot exceed 10,000 bounces."}),
            (_BOUNCES, {"ErrorCode": 1000, "Message": "A search can return at most 10,000 bounces."}),
            (_BOUNCES, {"ErrorCode": 1000, "Message": "Search results are limited to 10000 bounces."}),
        )
        for stream_name, error in cases:
            with self.subTest(stream=stream_name, message=error["Message"]), HttpMocker() as http_mocker:
                window = _stream_request(stream_name, "2025-01-02T06:00:00", "2025-01-02T06:55:01")
                http_mocker.get(window, HttpResponse(body=json.dumps(error), status_code=422))

                output = _read_stream(stream_name, SyncMode.incremental, config)

                assert output.records == []
                _assert_config_error(
                    output, f"Postmark's 10,000-record search limit was reached in one 60-minute window. {_LOWER_WINDOW_GUIDANCE}"
                )
                http_mocker.assert_number_of_calls(window, 1)

    @HttpMocker()
    def test_other_422_responses_fail_without_retry(self, http_mocker):
        config = ConfigBuilder().with_start_date("2025-01-02T11:00:00Z").build()
        # ErrorCode 700 (messages) and 1000 (bounces) cover every query validation error; only the offset limit is fixed by a smaller window.
        cases = (
            (_MESSAGES, 700, "Invalid date filter."),
            (_BOUNCES, 1000, "Illegal bounce type."),
        )
        for stream_name, error_code, message in cases:
            request = _stream_request(stream_name, "2025-01-02T06:00:00", "2025-01-02T06:55:01")
            http_mocker.get(
                request,
                HttpResponse(body=json.dumps({"ErrorCode": error_code, "Message": message}), status_code=422),
            )

            output = _read_stream(stream_name, SyncMode.incremental, config)

            assert any(
                error.trace.error.message == f"Postmark rejected the request (ErrorCode {error_code}): {message}" for error in output.errors
            )
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
