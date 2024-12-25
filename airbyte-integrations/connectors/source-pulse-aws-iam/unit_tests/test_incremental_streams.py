import pytest
from airbyte_cdk.models import SyncMode
from source_pulse_aws_iam.streams import CloudTrailEventsStream
from datetime import datetime


@pytest.fixture
def config():
    return {
        "provider": {
            "auth_type": "credentials",
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "region": "us-east-1",
            "start_time": "2024-01-01T00:00:00Z"
        }
    }


def test_cursor_field(config):
    stream = CloudTrailEventsStream(config)
    assert stream.cursor_field == "EventTime"


def test_get_lookup_attributes_with_state(config):
    stream = CloudTrailEventsStream(config)
    state = {"EventTime": "2024-02-01T00:00:00Z"}

    lookup_attrs = stream.get_lookup_attributes(state)
    assert "StartTime" in lookup_attrs
    assert isinstance(lookup_attrs["StartTime"], datetime)
    assert lookup_attrs["StartTime"].isoformat() + "Z" == "2024-02-01T00:00:00Z"


def test_get_lookup_attributes_with_config_start_time(config):
    stream = CloudTrailEventsStream(config)
    lookup_attrs = stream.get_lookup_attributes({})

    assert "StartTime" in lookup_attrs
    assert isinstance(lookup_attrs["StartTime"], datetime)
    assert lookup_attrs["StartTime"].isoformat() + "Z" == "2024-01-01T00:00:00Z"


def test_get_lookup_attributes_no_start_time():
    config_without_start = {
        "provider": {
            "auth_type": "credentials",
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "region": "us-east-1"
        }
    }
    stream = CloudTrailEventsStream(config_without_start)
    lookup_attrs = stream.get_lookup_attributes({})

    assert "StartTime" not in lookup_attrs


def test_read_records_handles_errors(mocker, config):
    mock_client = mocker.MagicMock()
    mock_paginator = mocker.MagicMock()
    mock_paginator.paginate.side_effect = Exception("Test error")
    mock_client.get_paginator.return_value = mock_paginator

    stream = CloudTrailEventsStream(config)
    stream.cloudtrail_client = mock_client

    records = list(stream.read_records(sync_mode=SyncMode.incremental))
    assert len(records) == 0


def test_read_records_success(mocker, config):
    mock_client = mocker.MagicMock()
    mock_paginator = mocker.MagicMock()
    mock_paginator.paginate.return_value = [{
        "Events": [
            {
                "EventId": "test-event-1",
                "EventTime": "2024-01-01T12:00:00Z"
            }
        ]
    }]
    mock_client.get_paginator.return_value = mock_paginator

    stream = CloudTrailEventsStream(config)
    stream.cloudtrail_client = mock_client

    records = list(stream.read_records(sync_mode=SyncMode.incremental))
    assert len(records) == 1
    assert records[0]["EventId"] == "test-event-1"
