#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime as dt
from unittest.mock import MagicMock

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
    now = int(dt.datetime.utcnow().timestamp() * 1000)
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


def test_stream_slices(log_stream):
    current_time = int(dt.datetime.utcnow().timestamp() * 1000)
    stream_state = {"timestamp": current_time - 3600000}

    slices = list(log_stream.stream_slices(sync_mode=None, stream_state=stream_state))

    assert len(slices) == 1
    assert "start_time" in slices[0]
    assert "end_time" in slices[0]
    assert slices[0]["start_time"] >= stream_state["timestamp"]
