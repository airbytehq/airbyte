# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest
from destination_biggeo.destination import DestinationBiggeo

from airbyte_cdk.models import Status


@pytest.fixture
def valid_config():
    return {
        "api_key": "test-api-key",
        "batch_size": 100,
    }


@pytest.fixture
def invalid_config():
    return {
        "api_key": "",
    }


def test_check_connection_missing_api_key():
    """Test that check fails when API key is missing."""
    destination = DestinationBiggeo()
    config = {}

    status = destination.check(logger=MagicMock(), config=config)
    assert status.status == Status.FAILED
    assert "API Key is required" in status.message


def test_get_headers():
    """Test that headers are correctly generated."""
    destination = DestinationBiggeo()
    api_key = "test-api-key"

    headers = destination._get_headers(api_key)

    assert headers["Content-Type"] == "application/json"
    assert headers["x-api-key"] == api_key


def test_check_connection_with_mock_success(valid_config):
    """Test successful connection check with mocked API response."""
    destination = DestinationBiggeo()

    with patch.object(destination, "_make_api_request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "SUCCEEDED"}
        mock_request.return_value = mock_response

        status = destination.check(logger=MagicMock(), config=valid_config)

        assert status.status == Status.SUCCEEDED
        mock_request.assert_called_once()


def test_check_connection_with_mock_failure(valid_config):
    """Test failed connection check with mocked API response."""
    destination = DestinationBiggeo()

    with patch.object(destination, "_make_api_request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "FAILED", "message": "Invalid credentials"}
        mock_request.return_value = mock_response

        status = destination.check(logger=MagicMock(), config=valid_config)

        assert status.status == Status.FAILED
        assert "Invalid credentials" in status.message


def test_base_url_is_used(valid_config):
    """Test that the hardcoded base URL is used correctly."""
    destination = DestinationBiggeo()

    with patch.object(destination, "_make_api_request") as mock_request:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "SUCCEEDED"}
        mock_request.return_value = mock_response

        destination.check(logger=MagicMock(), config=valid_config)

        call_args = mock_request.call_args
        assert "https://studio.biggeo.com/data-sources/v1/check-connection" in call_args[0][1]
