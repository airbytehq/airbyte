#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_cloudwatch_logs.source import SourceCloudwatchLogs


@pytest.fixture
def sample_config():
    return {"region_name": "us-east-1", "log_group_name": "example-group"}


@pytest.fixture
def source():
    return SourceCloudwatchLogs()


def test_check_connection_success(source, sample_config):
    # Patch boto3 client and its describe_log_groups method for success
    with patch("source_cloudwatch_logs.source.boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client = mock_client
        mock_logs_client = MagicMock()
        mock_client.return_value = mock_logs_client
        # Simulate a successful describe_log_groups call
        mock_logs_client.describe_log_groups.return_value = {"logGroups": [{"logGroupName": "example-group"}]}

        success, error = source.check_connection(None, sample_config)
        assert success is True
        assert error is None


def test_check_connection_failure(source, sample_config):
    # Patch boto3 client to raise exception on describe_log_groups (simulate bad credentials or network)
    with patch("source_cloudwatch_logs.source.boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client = mock_client
        mock_logs_client = MagicMock()
        mock_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.side_effect = Exception("Auth failed")

        success, error = source.check_connection(None, sample_config)
        assert success is False
        assert "Auth failed" in str(error)


def test_streams_dynamic_log_groups(source, sample_config):
    # Patch _get_log_group_names to simulate multiple log groups
    with patch.object(source, "_get_log_group_names", return_value=["group1", "group2"]):
        streams = source.streams(sample_config)
        assert len(streams) == 2
        # Each stream must have a log_group_name attribute set
        assert getattr(streams[0], "log_group_name", None) == "group1"
        assert getattr(streams[1], "log_group_name", None) == "group2"
