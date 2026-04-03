#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_shiftbase.streams import (
    Absentees,
    Departments,
    ShiftbaseStream,
    Shifts,
)


@pytest.fixture
def mock_accounts():
    """Fixture providing mock account configuration."""
    return [{"access_token": "test_token_123", "account_name": "test_account"}]


@pytest.fixture
def mock_start_date():
    """Fixture providing a mock start date."""
    return "2024-01-01"


@pytest.fixture
def patch_base_class(mocker):
    """Mock abstract methods to enable instantiating abstract class."""
    mocker.patch.object(ShiftbaseStream, "path", "v0/example_endpoint")
    mocker.patch.object(ShiftbaseStream, "primary_key", "test_primary_key")
    mocker.patch.object(ShiftbaseStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, mock_accounts, mock_start_date):
    """Test that request_params returns expected parameters."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"min_date": mock_start_date}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token_single_account(patch_base_class, mock_accounts, mock_start_date):
    """Test next_page_token returns None for single account."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    response_mock = MagicMock()
    # With single account, should return None after first request
    assert stream.next_page_token(response_mock) is None


def test_next_page_token_multiple_accounts(patch_base_class, mock_start_date):
    """Test next_page_token iterates through multiple accounts."""
    accounts = [
        {"access_token": "token1", "account_name": "account1"},
        {"access_token": "token2", "account_name": "account2"},
    ]
    stream = ShiftbaseStream(accounts=accounts, start_date=mock_start_date)
    response_mock = MagicMock()

    # First call should return next account token
    token = stream.next_page_token(response_mock)
    assert token == {"account_index": 1}
    assert stream.current_account["account_name"] == "account2"

    # Second call should return None (no more accounts)
    assert stream.next_page_token(response_mock) is None


def test_request_headers(patch_base_class, mock_accounts, mock_start_date):
    """Test that request_headers includes authorization."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    headers = stream.request_headers(**inputs)

    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"
    assert "Authorization" in headers
    assert headers["Authorization"] == "API test_token_123"


def test_http_method(patch_base_class, mock_accounts, mock_start_date):
    """Test default HTTP method is GET."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
        (HTTPStatus.BAD_GATEWAY, True),
        (HTTPStatus.SERVICE_UNAVAILABLE, True),
        (HTTPStatus.GATEWAY_TIMEOUT, True),
        (HTTPStatus.UNAUTHORIZED, False),
    ],
)
def test_should_retry(patch_base_class, mock_accounts, mock_start_date, http_status, should_retry):
    """Test retry logic for various HTTP status codes."""
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time_rate_limit(patch_base_class, mock_accounts, mock_start_date):
    """Test backoff time for rate limit response."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    response_mock = MagicMock()
    response_mock.status_code = 429
    response_mock.headers = {"Retry-After": "60"}

    backoff = stream.backoff_time(response_mock)
    assert backoff == 60.0


def test_backoff_time_server_error(patch_base_class, mock_accounts, mock_start_date):
    """Test backoff time for server error."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    response_mock = MagicMock()
    response_mock.status_code = 500
    response_mock.headers = {}

    backoff = stream.backoff_time(response_mock)
    assert backoff == stream.default_retry_delay


def test_backoff_time_normal_response(patch_base_class, mock_accounts, mock_start_date):
    """Test backoff time returns None for normal response."""
    stream = ShiftbaseStream(accounts=mock_accounts, start_date=mock_start_date)
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.headers = {}

    backoff = stream.backoff_time(response_mock)
    assert backoff is None


def test_departments_path(mock_accounts, mock_start_date):
    """Test Departments stream path."""
    stream = Departments(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.path() == "departments"


def test_departments_parse_response(mock_accounts, mock_start_date):
    """Test Departments stream parse_response."""
    stream = Departments(accounts=mock_accounts, start_date=mock_start_date)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"Department": {"id": "dept1", "name": "Engineering"}}, {"Department": {"id": "dept2", "name": "Sales"}}]
    }

    records = list(stream.parse_response(mock_response))
    assert len(records) == 2
    assert records[0]["id"] == "dept1"
    assert records[0]["account_name"] == "test_account"


def test_shifts_path(mock_accounts, mock_start_date):
    """Test Shifts stream path."""
    stream = Shifts(accounts=mock_accounts, start_date=mock_start_date)
    assert stream.path() == "shifts"


def test_absentees_incremental_properties(mock_accounts, mock_start_date):
    """Test Absentees stream has incremental sync properties."""
    from airbyte_cdk.models import SyncMode

    stream = Absentees(accounts=mock_accounts, start_date=mock_start_date)

    assert stream.cursor_field == "updated"
    assert stream.source_defined_cursor is True
    assert SyncMode.incremental in stream.supported_sync_modes
