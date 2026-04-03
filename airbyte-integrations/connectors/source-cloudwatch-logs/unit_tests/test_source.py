#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, call, patch

import pytest
from source_cloudwatch_logs.source import SourceCloudwatchLogs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def source():
    return SourceCloudwatchLogs()


@pytest.fixture
def base_config():
    return {"region_name": "us-east-1"}


@pytest.fixture
def config_with_role(base_config):
    return {
        **base_config,
        "role_arn": "arn:aws:iam::123456789012:role/MyRole",
    }


@pytest.fixture
def mock_sts_response():
    return {
        "Credentials": {
            "AccessKeyId": "ASIA_FAKE_KEY",
            "SecretAccessKey": "fake-secret",
            "SessionToken": "fake-token",
        }
    }


# ---------------------------------------------------------------------------
# _assume_role_session
# ---------------------------------------------------------------------------
class TestAssumeRoleSession:
    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_no_role_arn_returns_base_session(self, mock_boto_session, base_config):
        mock_session = MagicMock()
        mock_boto_session.return_value = mock_session

        result = SourceCloudwatchLogs._assume_role_session(base_config)

        assert result is mock_session
        mock_session.client.assert_not_called()

    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_role_arn_calls_sts_assume_role(self, mock_boto_session, config_with_role, mock_sts_response):
        mock_base_session = MagicMock()
        mock_assumed_session = MagicMock()
        mock_boto_session.side_effect = [mock_base_session, mock_assumed_session]

        mock_sts_client = MagicMock()
        mock_base_session.client.return_value = mock_sts_client
        mock_sts_client.assume_role.return_value = mock_sts_response

        result = SourceCloudwatchLogs._assume_role_session(config_with_role)

        mock_sts_client.assume_role.assert_called_once_with(
            RoleArn=config_with_role["role_arn"],
            RoleSessionName="airbyte-cloudwatch-session",
            DurationSeconds=3600,
        )
        assert result is mock_assumed_session

    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_role_arn_builds_session_from_credentials(self, mock_boto_session, config_with_role, mock_sts_response):
        mock_base_session = MagicMock()
        mock_boto_session.side_effect = [mock_base_session, MagicMock()]
        mock_sts_client = MagicMock()
        mock_base_session.client.return_value = mock_sts_client
        mock_sts_client.assume_role.return_value = mock_sts_response

        SourceCloudwatchLogs._assume_role_session(config_with_role)

        creds = mock_sts_response["Credentials"]
        mock_boto_session.assert_called_with(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=config_with_role["region_name"],
        )

    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_custom_role_session_duration_passed_to_assume_role(self, mock_boto_session, config_with_role, mock_sts_response):
        config_with_role["role_session_duration"] = 7200
        mock_base_session = MagicMock()
        mock_boto_session.side_effect = [mock_base_session, MagicMock()]
        mock_sts_client = MagicMock()
        mock_base_session.client.return_value = mock_sts_client
        mock_sts_client.assume_role.return_value = mock_sts_response

        SourceCloudwatchLogs._assume_role_session(config_with_role)

        call_kwargs = mock_sts_client.assume_role.call_args.kwargs
        assert call_kwargs["DurationSeconds"] == 7200


# ---------------------------------------------------------------------------
# _check_config
# ---------------------------------------------------------------------------
class TestCheckConfig:
    def test_no_custom_log_reports_key_does_not_raise(self, base_config):
        SourceCloudwatchLogs._check_config(base_config)  # should not raise

    def test_empty_custom_log_reports_does_not_raise(self, base_config):
        SourceCloudwatchLogs._check_config({**base_config, "custom_log_reports": []})

    def test_unique_custom_names_does_not_raise(self, base_config):
        config = {
            **base_config,
            "custom_log_reports": [
                {"name": "report-a", "log_group_name": "/aws/lambda/a"},
                {"name": "report-b", "log_group_name": "/aws/lambda/b"},
            ],
        }
        SourceCloudwatchLogs._check_config(config)  # should not raise

    def test_duplicate_custom_names_raises_value_error(self, base_config):
        config = {
            **base_config,
            "custom_log_reports": [
                {"name": "duplicate", "log_group_name": "/aws/lambda/a"},
                {"name": "duplicate", "log_group_name": "/aws/lambda/b"},
            ],
        }
        with pytest.raises(ValueError, match="unique"):
            SourceCloudwatchLogs._check_config(config)


# ---------------------------------------------------------------------------
# check_connection
# ---------------------------------------------------------------------------
class TestCheckConnection:
    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_uses_describe_log_streams_when_prefix_given(self, mock_boto_session, source):
        config = {"region_name": "us-east-1", "log_group_prefix": "/aws/lambda"}
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client

        success, error = source.check_connection(None, config)

        mock_client.describe_log_streams.assert_called_once_with(logGroupPrefix="/aws/lambda")
        mock_client.describe_log_groups.assert_not_called()
        assert success is True

    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_uses_describe_log_groups_when_no_prefix(self, mock_boto_session, source, base_config):
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client

        success, error = source.check_connection(None, base_config)

        mock_client.describe_log_groups.assert_called_once_with(limit=1)
        mock_client.describe_log_streams.assert_not_called()
        assert success is True

    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_check_config_error_returns_false(self, mock_boto_session, source, base_config):
        config = {
            **base_config,
            "custom_log_reports": [
                {"name": "dup", "log_group_name": "/aws/lambda/a"},
                {"name": "dup", "log_group_name": "/aws/lambda/b"},
            ],
        }

        success, error = source.check_connection(None, config)

        assert success is False
        assert "unique" in error.lower()

    @patch("source_cloudwatch_logs.source.boto3.Session")
    def test_aws_exception_returns_false(self, mock_boto_session, source, base_config):
        mock_client = MagicMock()
        mock_boto_session.return_value.client.return_value = mock_client
        mock_client.describe_log_groups.side_effect = Exception("Auth failed")

        success, error = source.check_connection(None, base_config)

        assert success is False
        assert "Auth failed" in error


# ---------------------------------------------------------------------------
# _get_log_group_names
# ---------------------------------------------------------------------------
class TestGetLogGroupNames:
    def _make_session(self, pages):
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_session.client.return_value = mock_client
        mock_paginator = MagicMock()
        mock_client.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = pages
        return mock_session, mock_paginator

    def test_returns_all_group_names_across_pages(self, base_config):
        pages = [
            {"logGroups": [{"logGroupName": "/aws/lambda/fn1"}, {"logGroupName": "/aws/lambda/fn2"}]},
            {"logGroups": [{"logGroupName": "/aws/lambda/fn3"}]},
        ]
        mock_session, _ = self._make_session(pages)

        result = SourceCloudwatchLogs._get_log_group_names(base_config, mock_session)

        assert result == ["/aws/lambda/fn1", "/aws/lambda/fn2", "/aws/lambda/fn3"]

    def test_empty_pages_returns_empty_list(self, base_config):
        mock_session, _ = self._make_session([{"logGroups": []}])

        result = SourceCloudwatchLogs._get_log_group_names(base_config, mock_session)

        assert result == []

    def test_no_prefix_paginates_without_prefix_kwarg(self, base_config):
        mock_session, mock_paginator = self._make_session([{"logGroups": []}])

        SourceCloudwatchLogs._get_log_group_names(base_config, mock_session)

        mock_paginator.paginate.assert_called_once_with()

    def test_prefix_passed_to_paginator(self, base_config):
        config = {**base_config, "log_group_prefix": "/aws/lambda"}
        mock_session, mock_paginator = self._make_session([{"logGroups": []}])

        SourceCloudwatchLogs._get_log_group_names(config, mock_session)

        mock_paginator.paginate.assert_called_once_with(logGroupNamePrefix="/aws/lambda")


# ---------------------------------------------------------------------------
# streams
# ---------------------------------------------------------------------------
class TestStreams:
    @patch.object(SourceCloudwatchLogs, "_get_log_group_names", return_value=["group1", "group2"])
    @patch.object(SourceCloudwatchLogs, "_assume_role_session")
    def test_streams_created_for_each_log_group(self, mock_session, mock_groups, source, base_config):
        streams = source.streams(base_config)

        assert len(streams) == 2
        assert streams[0].log_group_name == "group1"
        assert streams[1].log_group_name == "group2"

    @patch.object(SourceCloudwatchLogs, "_get_log_group_names", return_value=[])
    @patch.object(SourceCloudwatchLogs, "_assume_role_session")
    def test_custom_log_reports_appended_to_streams(self, mock_session, mock_groups, source, base_config):
        config = {
            **base_config,
            "custom_log_reports": [
                {
                    "name": "my-report",
                    "log_group_name": "/aws/lambda/custom",
                    "log_stream_names": ["stream-x"],
                    "filter_pattern": "ERROR",
                },
            ],
        }

        streams = source.streams(config)

        assert len(streams) == 1
        s = streams[0]
        assert s.name == "my-report"
        assert s.log_group_name == "/aws/lambda/custom"
        assert s.kwargs.get("logStreamNames") == ["stream-x"]
        assert s.kwargs.get("filterPattern") == "ERROR"

    @patch.object(SourceCloudwatchLogs, "_get_log_group_names", return_value=["group1"])
    @patch.object(SourceCloudwatchLogs, "_assume_role_session")
    def test_start_date_passed_to_all_streams(self, mock_session, mock_groups, source, base_config):
        config = {**base_config, "start_date": "2026-01-01T00:00:00Z"}

        streams = source.streams(config)

        assert all(s.start_date == 1767225600000 for s in streams)

    @patch.object(SourceCloudwatchLogs, "_get_log_group_names", return_value=["group1"])
    @patch.object(SourceCloudwatchLogs, "_assume_role_session")
    def test_no_start_date_gives_none(self, mock_session, mock_groups, source, base_config):
        streams = source.streams(base_config)

        assert all(s.start_date is None for s in streams)

    @patch.object(SourceCloudwatchLogs, "_get_log_group_names", return_value=["group1"])
    @patch.object(SourceCloudwatchLogs, "_assume_role_session")
    def test_no_custom_log_reports_returns_only_discovered_streams(self, mock_session, mock_groups, source, base_config):
        streams = source.streams(base_config)

        assert len(streams) == 1
        assert streams[0].log_group_name == "group1"

    @patch.object(SourceCloudwatchLogs, "_get_log_group_names", return_value=["group1"])
    @patch.object(SourceCloudwatchLogs, "_assume_role_session")
    def test_combined_discovered_and_custom_streams(self, mock_session, mock_groups, source, base_config):
        config = {
            **base_config,
            "custom_log_reports": [{"name": "custom", "log_group_name": "/aws/lambda/custom"}],
        }

        streams = source.streams(config)

        assert len(streams) == 2
        assert streams[0].log_group_name == "group1"
        assert streams[1].name == "custom"
