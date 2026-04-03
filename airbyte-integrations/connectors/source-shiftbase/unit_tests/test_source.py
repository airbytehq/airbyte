#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_shiftbase.source import SourceShiftbase


@pytest.fixture
def mock_config():
    """Fixture providing a valid configuration for tests."""
    return {"accounts": [{"access_token": "test_token_123", "account_name": "test_account"}], "start_date": "2024-01-01"}


@pytest.fixture
def mock_config_multiple_accounts():
    """Fixture providing configuration with multiple accounts."""
    return {
        "accounts": [
            {"access_token": "test_token_1", "account_name": "account_1"},
            {"access_token": "test_token_2", "account_name": "account_2"},
        ],
        "start_date": "2024-01-01",
    }


def test_check_connection_success(mocker, mock_config):
    """Test successful connection check."""
    source = SourceShiftbase()
    logger_mock = MagicMock()

    # Mock the requests.get call to return a successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mocker.patch("requests.get", return_value=mock_response)

    result, error = source.check_connection(logger_mock, mock_config)
    assert result is True
    assert error is None


def test_check_connection_failure_no_accounts(mocker):
    """Test connection check fails when no accounts configured."""
    source = SourceShiftbase()
    logger_mock = MagicMock()
    config = {"accounts": [], "start_date": "2024-01-01"}

    result, error = source.check_connection(logger_mock, config)
    assert result is False
    assert "No accounts configured" in error


def test_check_connection_failure_missing_token(mocker):
    """Test connection check fails when access_token is missing."""
    source = SourceShiftbase()
    logger_mock = MagicMock()
    config = {"accounts": [{"account_name": "test"}], "start_date": "2024-01-01"}

    result, error = source.check_connection(logger_mock, config)
    assert result is False
    assert "Missing access_token or account_name" in error


def test_check_connection_api_failure(mocker, mock_config):
    """Test connection check handles API errors."""
    source = SourceShiftbase()
    logger_mock = MagicMock()

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mocker.patch("requests.get", return_value=mock_response)

    result, error = source.check_connection(logger_mock, mock_config)
    assert result is False
    assert "401" in error


def test_streams_returns_expected_streams(mocker, mock_config):
    """Test that streams method returns all expected streams."""
    source = SourceShiftbase()

    # Mock the department and employee extraction to avoid API calls
    mocker.patch.object(source, "extract_department_ids", return_value=[])
    mocker.patch.object(source, "extract_employee_ids", return_value=[])

    streams = source.streams(mock_config)

    # Should return 10 streams
    expected_streams_number = 10
    assert len(streams) == expected_streams_number

    # Verify stream names
    stream_names = [stream.name for stream in streams]
    expected_names = [
        "departments",
        "employees",
        "absentees",
        "employee_time_distribution",
        "availabilities",
        "shifts",
        "users",
        "employees_report",
        "timesheet_detail_report",
        "schedule_detail_report",
    ]
    for name in expected_names:
        assert name in stream_names, f"Expected stream '{name}' not found"
