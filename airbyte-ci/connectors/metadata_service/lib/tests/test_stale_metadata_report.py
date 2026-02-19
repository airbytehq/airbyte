#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import Mock, patch

import pytest
import yaml as real_yaml

from metadata_service.constants import PUBLISH_GRACE_PERIOD
from metadata_service.stale_metadata_report import (
    _generate_stale_metadata_report,
    _get_latest_metadata_entries_on_gcs,
    _get_latest_metadata_versions_on_github,
    _is_younger_than_grace_period,
    generate_and_publish_stale_metadata_report,
)

pytest_plugins = ["tests.fixtures.stale_metadata_report_fixtures"]


def _mock_commits(old_datetime):
    commit = Mock()
    commit.commit = Mock()
    commit.commit.author = Mock()
    commit.commit.author.date = old_datetime
    return [commit]


def mock_get(url, yaml_responses):
    mock_response = Mock()
    mock_response.text = yaml_responses[url]
    mock_response.raise_for_status = Mock()
    return mock_response


def mock_safe_load(yaml_text: str):
    return real_yaml.safe_load(yaml_text)


@pytest.mark.parametrize(
    "hours_offset,expected_result",
    [
        (-1, False),
        (0, False),
        (1, True),
    ],
)
def test_is_younger_than_grace_period_parameterized(hours_offset, expected_result):
    """Test _is_younger_than_grace_period with different time offsets relative to grace period."""
    grace_period_marker = datetime.datetime.now(datetime.timezone.utc) - PUBLISH_GRACE_PERIOD
    test_datetime = grace_period_marker + datetime.timedelta(hours=hours_offset)

    mock_last_modified_at_date_time = test_datetime

    result = _is_younger_than_grace_period(mock_last_modified_at_date_time)
    assert result == expected_result


@pytest.mark.parametrize(
    "github_versions,gcs_versions,expected_stale_count,description",
    [
        ({}, {}, 0, "empty mappings"),
        ({"connector-a": "1.0.0"}, {"connector-a": "1.0.0"}, 0, "identical versions"),
        ({"connector-a": "1.1.0"}, {"connector-a": "1.0.0"}, 1, "github newer than gcs"),
        ({"connector-a": "1.0.0"}, {}, 1, "missing from gcs"),
        ({}, {"connector-a": "1.0.0"}, 0, "missing from github - not reported"),
        ({"connector-a": "1.1.0", "connector-b": "2.0.0"}, {"connector-a": "1.0.0", "connector-b": "2.0.0"}, 1, "mixed scenarios"),
    ],
)
def test_generate_stale_metadata_report_parameterized(github_versions, gcs_versions, expected_stale_count, description):
    """Test _generate_stale_metadata_report with different version mapping scenarios."""
    result_df = _generate_stale_metadata_report(github_versions, gcs_versions)

    assert len(result_df) == expected_stale_count, f"Failed for {description}"

    if expected_stale_count > 0:
        expected_columns = ["connector", "master_version", "gcs_version"]
        assert list(result_df.columns) == expected_columns, f"Incorrect columns for {description}"

        for _, row in result_df.iterrows():
            connector = row["connector"]
            github_version = row["master_version"]
            gcs_version = row["gcs_version"]

            assert connector in github_versions, f"Connector {connector} not in GitHub versions"
            assert github_versions[connector] == github_version, f"GitHub version mismatch for {connector}"
            assert github_version != gcs_version, f"Versions should be different for stale connector {connector}"


def test_get_latest_metadata_versions_on_github_success(mock_github_files, mock_yaml_responses):
    """Test _get_latest_metadata_versions_on_github successfully retrieves and filters metadata."""
    with (
        patch("os.getenv") as mock_getenv,
        patch("metadata_service.stale_metadata_report.Auth") as mock_auth,
        patch("metadata_service.stale_metadata_report.Github") as mock_github,
        patch("metadata_service.stale_metadata_report.requests") as mock_requests,
        patch("metadata_service.stale_metadata_report.yaml") as mock_yaml,
    ):
        mock_getenv.return_value = "test-github-token"
        mock_auth.Token.return_value = Mock()

        mock_github_client = Mock()
        mock_repo = Mock()
        mock_github.return_value = mock_github_client
        mock_github_client.get_repo.return_value = mock_repo

        # Configure search_code to return our mock file list
        mock_github_client.search_code.return_value = mock_github_files

        # Each call to repo.get_commits(path=...) should return a commit list with an old datetime
        old_datetime = datetime.datetime.now(datetime.timezone.utc) - PUBLISH_GRACE_PERIOD - datetime.timedelta(hours=1)

        mock_repo.full_name = "airbyte/airbyte"
        mock_repo.get_commits.side_effect = lambda path: _mock_commits(old_datetime)

        mock_requests.get.side_effect = lambda url: mock_get(url, mock_yaml_responses)

        mock_yaml.safe_load = mock_safe_load

        result = _get_latest_metadata_versions_on_github()

        expected_result = {"airbyte/source-test-1": "1.0.0"}

        assert result == expected_result
        mock_getenv.assert_called_once_with("GITHUB_TOKEN")
        mock_github_client.get_repo.assert_called_once()
        mock_github_client.search_code.assert_called_once()
        assert mock_requests.get.call_count == 3


def test_get_latest_metadata_entries_on_gcs_success(mock_gcs_blobs):
    """Test _get_latest_metadata_entries_on_gcs successfully retrieves metadata from GCS."""
    with (
        patch("metadata_service.stale_metadata_report.get_gcs_storage_client") as mock_get_client,
        patch("metadata_service.stale_metadata_report.yaml") as mock_yaml,
    ):
        mock_storage_client = Mock()
        mock_bucket = Mock()
        mock_get_client.return_value = mock_storage_client
        mock_storage_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = mock_gcs_blobs

        mock_yaml.safe_load = mock_safe_load

        result = _get_latest_metadata_entries_on_gcs("test-bucket")

        expected_result = {"airbyte/source-gcs-1": "1.2.0", "airbyte/source-gcs-2": "2.1.0", "airbyte/destination-gcs-1": "3.0.0"}

        assert result == expected_result
        mock_get_client.assert_called_once()
        mock_storage_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.list_blobs.assert_called_once()
        assert all(blob.download_as_bytes.called for blob in mock_gcs_blobs)


def test_generate_and_publish_stale_metadata_report_with_stale_data():
    """Test main workflow when stale metadata is detected."""
    with (
        patch("metadata_service.stale_metadata_report.STALE_REPORT_CHANNEL", "123456789"),
        patch("metadata_service.stale_metadata_report.PUBLISH_UPDATE_CHANNEL", "987654321"),
        patch("metadata_service.stale_metadata_report._get_latest_metadata_versions_on_github") as mock_github,
        patch("metadata_service.stale_metadata_report._get_latest_metadata_entries_on_gcs") as mock_gcs,
        patch("metadata_service.stale_metadata_report.send_slack_message", return_value=(True, None)) as mock_slack,
        patch("pandas.DataFrame.to_markdown") as mock_to_markdown,
    ):
        mock_github.return_value = {"connector-a": "2.0.0", "connector-b": "1.5.0"}
        mock_gcs.return_value = {"connector-a": "1.0.0", "connector-b": "1.5.0"}
        mock_to_markdown.return_value = (
            "| connector | master_version | gcs_version |\n|-----------|----------------|-------------|\n| connector-a | 2.0.0 | 1.0.0 |"
        )

        result = generate_and_publish_stale_metadata_report("test-bucket")

        assert result == (True, None)
        assert mock_slack.call_count == 2

        alert_call = mock_slack.call_args_list[0]
        assert "123456789" in str(alert_call)
        assert "Stale metadata detected" in alert_call[0][1]

        report_call = mock_slack.call_args_list[1]
        assert "123456789" in str(report_call)
        assert report_call[1]["enable_code_block_wrapping"] is True


def test_generate_and_publish_stale_metadata_report_no_stale_data():
    """Test main workflow when no stale metadata is detected."""
    with (
        patch("metadata_service.stale_metadata_report.STALE_REPORT_CHANNEL", "123456789"),
        patch("metadata_service.stale_metadata_report.PUBLISH_UPDATE_CHANNEL", "987654321"),
        patch("metadata_service.stale_metadata_report._get_latest_metadata_versions_on_github") as mock_github,
        patch("metadata_service.stale_metadata_report._get_latest_metadata_entries_on_gcs") as mock_gcs,
        patch("metadata_service.stale_metadata_report.send_slack_message", return_value=(True, None)) as mock_slack,
    ):
        mock_github.return_value = {"connector-a": "1.0.0", "connector-b": "1.5.0"}
        mock_gcs.return_value = {"connector-a": "1.0.0", "connector-b": "1.5.0"}

        result = generate_and_publish_stale_metadata_report("test-bucket")

        assert result == (True, None)
        mock_slack.assert_called_once()

        success_call = mock_slack.call_args_list[0]
        assert "987654321" in str(success_call)
        assert "No stale metadata" in success_call[0][1]


def test_generate_and_publish_stale_metadata_report_large_stale_report():
    """Test main workflow with a large number of stale connectors."""
    large_github_data = {f"airbyte/connector-{i:04d}": f"2.{i % 10}.0" for i in range(100)}
    large_gcs_data = {f"airbyte/connector-{i:04d}": f"1.{i % 10}.0" for i in range(100)}

    with (
        patch("metadata_service.stale_metadata_report._get_latest_metadata_versions_on_github") as mock_github,
        patch("metadata_service.stale_metadata_report._get_latest_metadata_entries_on_gcs") as mock_gcs,
        patch("metadata_service.stale_metadata_report.send_slack_message", return_value=(True, None)) as mock_slack,
        patch("pandas.DataFrame.to_markdown") as mock_to_markdown,
        patch("metadata_service.stale_metadata_report.STALE_REPORT_CHANNEL", "123456789"),
        patch("metadata_service.stale_metadata_report.PUBLISH_UPDATE_CHANNEL", "987654321"),
    ):
        mock_github.return_value = large_github_data
        mock_gcs.return_value = large_gcs_data
        mock_to_markdown.return_value = "Large markdown table with 100 stale connectors..."

        result = generate_and_publish_stale_metadata_report("test-bucket")

        assert result == (True, None)
        assert mock_slack.call_count == 2

        alert_call = mock_slack.call_args_list[0]
        assert "123456789" in str(alert_call)
        assert "Stale metadata detected" in alert_call[0][1]

        report_call = mock_slack.call_args_list[1]
        assert "123456789" in str(report_call)
        assert report_call[1]["enable_code_block_wrapping"] is True
