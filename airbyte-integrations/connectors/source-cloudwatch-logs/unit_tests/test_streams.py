#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime as dt
from unittest.mock import MagicMock, patch

import pytest
from source_cloudwatch_logs.streams import Logs


@pytest.fixture
def log_stream():
    mock_session = MagicMock()
    mock_client = MagicMock()
    mock_session.client.return_value = mock_client
    return Logs(
        region_name="us-east-1",
        log_group_name="/aws/lambda/test-func",
        session=mock_session,
    )


@pytest.fixture
def fake_events():
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


def test_name(log_stream):
    assert log_stream.name == "/aws/lambda/test-func"


def test_read_records(log_stream, fake_events):
    # Mock boto3 client and response
    log_stream.client.filter_log_events.return_value = {
        "events": fake_events,
        "nextToken": None,
    }

    stream_slice = {
        "start_time": fake_events[0]["timestamp"] - 1000,
        "end_time": fake_events[-1]["timestamp"] + 1000,
    }

    records = list(log_stream.read_records(sync_mode=None, stream_slice=stream_slice))

    assert len(records) == len(fake_events)
    assert records[0]["message"] == "First log message"
    assert records[1]["eventId"] == "evt2"


def test_setting_existing_state(log_stream):
    # Provide previous state
    log_stream.state = {"timestamp": 1234567890}
    assert log_stream._cursor_value == 1234567890


@patch(
    "source_cloudwatch_logs.streams.dt.datetime",
    return_value=dt.datetime(2026, 1, 1, tzinfo=dt.UTC),
)
def test_stream_slices_one_slice(mock_datetime, log_stream):
    # Stream slices splits the time range into 1 day slices. For a 1h range, it should return 1 slice

    mock_datetime.now.return_value = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    # 2026-01-01 00:00:00 UTC in milliseconds
    current_time = 1767225600000
    # 1 hour before current time
    stream_state = {"timestamp": current_time - 3600000}

    slices = list(log_stream.stream_slices(sync_mode=None, stream_state=stream_state))

    assert slices == [
        {
            "start_time": current_time - 3600000,
            "end_time": current_time,
        },
    ]


@patch(
    "source_cloudwatch_logs.streams.dt.datetime",
    return_value=dt.datetime(2026, 1, 1, tzinfo=dt.UTC),
)
def test_stream_slices_many_slices(mock_datetime, log_stream):
    # Stream slices splits the time range into 1 day slices. For a 2-day range, it should return 2 slices
    mock_datetime.now.return_value = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)

    # 2026-01-01 00:00:00 UTC in milliseconds
    current_time = 1767225600000
    # 2 days - 1ms before current time
    stream_state = {"timestamp": current_time - 172800000 + 1}

    slices = list(log_stream.stream_slices(sync_mode=None, stream_state=stream_state))

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
