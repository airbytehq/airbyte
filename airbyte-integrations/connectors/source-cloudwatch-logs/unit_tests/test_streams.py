#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime as dt
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from source_cloudwatch_logs.streams import Logs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_session():
    session = MagicMock()
    session.client.return_value = MagicMock()
    return session


@pytest.fixture
def mock_log_stream():
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client
    return Logs(
        region_name="us-east-1",
        log_group_name="/aws/lambda/test-func",
        session=mock_session,
    )


@pytest.fixture
def mock_events():
    now = int(dt.datetime.now(dt.UTC).timestamp() * 1000)
    return [
        {
            "timestamp": now - 10000,
            "message": "First log message",
            "logStreamName": "first-log-stream",
            "ingestionTime": now - 9000,
            "eventId": "evt1",
        },
        {
            "timestamp": now - 5000,
            "message": "Second log message",
            "logStreamName": "second-log-stream",
            "ingestionTime": now - 4000,
            "eventId": "evt2",
        },
    ]


# ---------------------------------------------------------------------------
# __init__ parameter handling
# ---------------------------------------------------------------------------
class TestInit:
    def test_log_stream_names_added_to_kwargs(self, mock_session):
        stream = Logs(
            region_name="us-east-1",
            log_group_name="/aws/lambda/test-func",
            session=mock_session,
            log_stream_names=["stream-a", "stream-b"],
        )
        assert stream.kwargs["logStreamNames"] == ["stream-a", "stream-b"]

    def test_filter_pattern_added_to_kwargs(self, mock_session):
        stream = Logs(
            region_name="us-east-1",
            log_group_name="/aws/lambda/test-func",
            session=mock_session,
            filter_pattern="ERROR",
        )
        assert stream.kwargs["filterPattern"] == "ERROR"

    def test_no_optional_kwargs_by_default(self, mock_log_stream):
        assert mock_log_stream.kwargs == {}

    def test_start_date_parsed_to_milliseconds(self, mock_session):
        stream = Logs(
            region_name="us-east-1",
            log_group_name="/aws/lambda/test-func",
            session=mock_session,
            start_date="2026-01-01T00:00:00Z",
        )
        assert stream.start_date == 1767225600000

    def test_no_start_date_is_none(self, mock_log_stream):
        assert mock_log_stream.start_date is None


# ---------------------------------------------------------------------------
# name property
# ---------------------------------------------------------------------------
class TestName:
    def test_name_defaults_to_log_group_name(self, mock_log_stream):
        assert mock_log_stream.name == "/aws/lambda/test-func"

    def test_custom_name_overrides_log_group_name(self, mock_session):
        stream = Logs(
            region_name="us-east-1",
            log_group_name="/aws/lambda/test-func",
            session=mock_session,
            name="my-custom-name",
        )
        assert stream.name == "my-custom-name"


# ---------------------------------------------------------------------------
# state property
# ---------------------------------------------------------------------------
class TestState:
    def test_state_is_empty_when_cursor_is_none(self, mock_log_stream):
        assert mock_log_stream.state == {}

    def test_state_returns_cursor_value_after_set(self, mock_log_stream):
        mock_log_stream.state = {"timestamp": 9999999}
        assert mock_log_stream.state == {"timestamp": 9999999}

    def test_state_setter_ignores_missing_cursor_field(self, mock_log_stream):
        mock_log_stream.state = {}
        assert mock_log_stream._cursor_value is None
        assert mock_log_stream.state == {}


# ---------------------------------------------------------------------------
# _get_start_timestamp
# ---------------------------------------------------------------------------
class TestGetStartTimestamp:
    def test_returns_none_when_no_events(self, mock_log_stream):
        mock_log_stream.client.filter_log_events.return_value = {"events": []}
        assert mock_log_stream._get_start_timestamp() is None

    def test_returns_earliest_timestamp_when_events_exist(self, mock_log_stream):
        mock_log_stream.client.filter_log_events.return_value = {"events": [{"timestamp": 1234567890000}]}
        assert mock_log_stream._get_start_timestamp() == 1234567890000

    def test_queries_from_time_zero(self, mock_log_stream):
        mock_log_stream.client.filter_log_events.return_value = {"events": []}
        mock_log_stream._get_start_timestamp()
        assert mock_log_stream.client.filter_log_events.call_args.kwargs["startTime"] == 0


# ---------------------------------------------------------------------------
# stream_slices
# ---------------------------------------------------------------------------
class TestStreamSlices:
    CURRENT_TIME = 1767225600000  # 2026-01-01 00:00:00 UTC in ms
    ONE_DAY_MS = 86400000

    @freeze_time("2026-01-01 00:00:00+00:00")
    def test_stream_slices_one_slice(self, mock_log_stream):
        # Stream slices splits the time range into 1 day slices. For a 1h range, it should return 1 slice
        # 2026-01-01 00:00:00 UTC in milliseconds
        current_time = 1767225600000
        # 1 hour before current time
        stream_state = {"timestamp": current_time - 3600000}

        slices = list(mock_log_stream.stream_slices(sync_mode=None, stream_state=stream_state))

        assert slices == [
            {
                "start_time": current_time - 3600000,
                "end_time": current_time,
            },
        ]

    @freeze_time("2026-01-01 00:00:00+00:00")
    def test_stream_slices_many_slices(self, mock_log_stream):
        # Stream slices splits the time range into 1 day slices. For a 2-day range, it should return 2 slices
        # 2026-01-01 00:00:00 UTC in milliseconds
        current_time = 1767225600000
        # 2 days - 1ms before current time
        stream_state = {"timestamp": current_time - 172800000 + 1}

        slices = list(mock_log_stream.stream_slices(sync_mode=None, stream_state=stream_state))

        assert slices == [
            {
                "start_time": current_time - 172800000 + 1,
                "end_time": current_time - 86400000,
            },
            {
                "start_time": current_time - 86400000 + 1,
                "end_time": current_time,
            },
        ]

    @freeze_time("2026-01-01 00:00:00+00:00")
    def test_no_state_no_start_date_no_events_returns_empty(self, mock_log_stream):
        mock_log_stream.client.filter_log_events.return_value = {"events": []}

        slices = list(mock_log_stream.stream_slices(sync_mode=None, stream_state={}))

        assert slices == []

    @freeze_time("2026-01-01 00:00:00+00:00")
    def test_uses_start_date_when_no_state(self, mock_session):
        stream = Logs(
            region_name="us-east-1",
            log_group_name="/aws/lambda/test-func",
            session=mock_session,
            start_date="2026-01-01T00:00:00Z",
        )

        slices = list(stream.stream_slices(sync_mode=None, stream_state={}))

        # start_date == current_time, so one slice with start == end
        assert slices == [
            {
                "start_time": self.CURRENT_TIME,
                "end_time": self.CURRENT_TIME,
            },
        ]

    @freeze_time("2026-01-01 00:00:00+00:00")
    def test_start_time_equals_current_time_yields_one_slice(self, mock_log_stream):
        stream_state = {"timestamp": self.CURRENT_TIME}

        slices = list(mock_log_stream.stream_slices(sync_mode=None, stream_state=stream_state))

        assert slices == [
            {
                "start_time": self.CURRENT_TIME,
                "end_time": self.CURRENT_TIME,
            },
        ]

    @freeze_time("2026-01-01 00:00:00+00:00")
    def test_falls_back_to_get_start_timestamp_when_no_state_or_start_date(self, mock_log_stream):
        # 1 hour before current_time
        earliest_ts = self.CURRENT_TIME - 3600000
        mock_log_stream.client.filter_log_events.return_value = {"events": [{"timestamp": earliest_ts}]}

        slices = list(mock_log_stream.stream_slices(sync_mode=None, stream_state={}))

        assert slices == [
            {
                "start_time": earliest_ts,
                "end_time": self.CURRENT_TIME,
            },
        ]


# ---------------------------------------------------------------------------
# read_records
# ---------------------------------------------------------------------------
class TestReadRecords:
    def test_read_records(self, mock_log_stream, mock_events):
        # Mock boto3 client and response
        mock_log_stream.client.filter_log_events.return_value = {
            "events": mock_events,
            "nextToken": None,
        }

        stream_slice = {
            "start_time": mock_events[0]["timestamp"] - 1000,
            "end_time": mock_events[-1]["timestamp"] + 1000,
        }

        records = list(mock_log_stream.read_records(sync_mode=None, stream_slice=stream_slice))

        assert len(records) == len(mock_events)
        assert records[0]["message"] == "First log message"
        assert records[1]["eventId"] == "evt2"

    def test_yields_no_records_for_empty_events(self, mock_log_stream):
        mock_log_stream.client.filter_log_events.return_value = {"events": [], "nextToken": None}
        records = list(mock_log_stream.read_records(sync_mode=None, stream_slice={}))
        assert records == []

    def test_cursor_value_set_to_max_timestamp(self, mock_log_stream, mock_events):
        # Ensure max is taken even if events arrive out of order
        out_of_order = [mock_events[1], mock_events[0]]  # higher ts first
        mock_log_stream.client.filter_log_events.return_value = {
            "events": out_of_order,
            "nextToken": None,
        }
        list(mock_log_stream.read_records(sync_mode=None, stream_slice={}))
        assert mock_log_stream._cursor_value == mock_events[1]["timestamp"]  # the max

    def test_cursor_set_for_single_event(self, mock_log_stream, mock_events):
        mock_log_stream.client.filter_log_events.return_value = {
            "events": [mock_events[0]],
            "nextToken": None,
        }
        list(mock_log_stream.read_records(sync_mode=None, stream_slice={}))
        assert mock_log_stream._cursor_value == mock_events[0]["timestamp"]

    def test_pagination_fetches_all_pages(self, mock_log_stream, mock_events):
        mock_log_stream.client.filter_log_events.side_effect = [
            {"events": [mock_events[0]], "nextToken": "token-abc"},
            {"events": [mock_events[1]], "nextToken": None},
        ]
        records = list(mock_log_stream.read_records(sync_mode=None, stream_slice={}))
        assert len(records) == 2
        assert mock_log_stream.client.filter_log_events.call_count == 2

    def test_pagination_passes_next_token(self, mock_log_stream, mock_events):
        mock_log_stream.client.filter_log_events.side_effect = [
            {"events": [mock_events[0]], "nextToken": "token-xyz"},
            {"events": [mock_events[1]], "nextToken": None},
        ]
        list(mock_log_stream.read_records(sync_mode=None, stream_slice={}))
        second_call_kwargs = mock_log_stream.client.filter_log_events.call_args_list[1][1]
        assert second_call_kwargs.get("nextToken") == "token-xyz"

    def test_extra_kwargs_passed_to_filter_log_events(self, mock_session, mock_events):
        stream = Logs(
            region_name="us-east-1",
            log_group_name="/aws/lambda/test-func",
            session=mock_session,
            filter_pattern="ERROR",
            log_stream_names=["stream-a"],
        )
        stream.client.filter_log_events.return_value = {"events": mock_events, "nextToken": None}
        list(stream.read_records(sync_mode=None, stream_slice={}))

        call_kwargs = stream.client.filter_log_events.call_args[1]
        assert call_kwargs.get("filterPattern") == "ERROR"
        assert call_kwargs.get("logStreamNames") == ["stream-a"]

    def test_cursor_not_regressed_by_older_event(self, mock_log_stream, mock_events):
        # Start with a high cursor value; reading older events should not lower it
        mock_log_stream._cursor_value = mock_events[1]["timestamp"]
        mock_log_stream.client.filter_log_events.return_value = {
            "events": [mock_events[0]],  # older timestamp
            "nextToken": None,
        }
        list(mock_log_stream.read_records(sync_mode=None, stream_slice={}))
        assert mock_log_stream._cursor_value == mock_events[1]["timestamp"]
