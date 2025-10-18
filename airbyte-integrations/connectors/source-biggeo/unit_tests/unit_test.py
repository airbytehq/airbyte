# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for BigGeo source connector."""

from unittest.mock import MagicMock, patch

import pytest
from source_biggeo.source import BigGeoStream, SourceBiggeo


@pytest.fixture
def valid_config():
    return {
        "api_key": "test-api-key",
        "data_source_name": "test_data_source",
    }


@pytest.fixture
def invalid_config():
    return {
        "api_key": "",
        "data_source_name": "test_data_source",
    }


@pytest.fixture
def source():
    return SourceBiggeo()


def test_check_connection_missing_api_key(source):
    """Test that check fails when API key is missing."""
    config = {"data_source_name": "test"}

    success, message = source.check_connection(logger=MagicMock(), config=config)

    assert success is False
    assert "API Key is required" in message


def test_check_connection_with_mock_success(source, valid_config):
    """Test successful connection check with mocked API response."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "SUCCEEDED"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        success, message = source.check_connection(logger=MagicMock(), config=valid_config)

        assert success is True
        assert message is None
        mock_get.assert_called_once()


def test_check_connection_with_mock_failure(source, valid_config):
    """Test failed connection check with mocked API response."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "FAILED", "message": "Invalid credentials"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        success, message = source.check_connection(logger=MagicMock(), config=valid_config)

        assert success is False
        assert "Invalid credentials" in message


def test_streams_with_data_source_name(source, valid_config):
    """Test that streams are created when data_source_name is provided."""
    streams = source.streams(config=valid_config)

    assert len(streams) == 1
    assert streams[0].name == "test_data_source"
    assert isinstance(streams[0], BigGeoStream)


def test_streams_without_data_source_name(source):
    """Test that no streams are created when data_source_name is not provided."""
    config = {"api_key": "test-api-key"}
    streams = source.streams(config=config)

    assert len(streams) == 0


def test_biggeo_stream_name():
    """Test that BigGeoStream returns correct name."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    assert stream.name == "my_data_source"


def test_biggeo_stream_headers():
    """Test that BigGeoStream returns correct headers."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    headers = stream._get_headers()

    assert headers["Content-Type"] == "application/json"
    assert headers["x-api-key"] == "test-key"


def test_biggeo_stream_read_records_array():
    """Test reading records when API returns an array."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "name": "record1"},
            {"id": 2, "name": "record2"},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        records = list(stream.read_records(sync_mode="full_refresh"))

        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[1]["id"] == 2
        mock_get.assert_called_once()


def test_biggeo_stream_read_records_object():
    """Test reading records when API returns a single object."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "record1"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        records = list(stream.read_records(sync_mode="full_refresh"))

        assert len(records) == 1
        assert records[0]["id"] == 1
        mock_get.assert_called_once()


def test_biggeo_stream_get_json_schema():
    """Test that get_json_schema returns a flexible schema."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    schema = stream.get_json_schema()

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is True


def test_biggeo_stream_url_construction():
    """Test that the correct URL is constructed."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        list(stream.read_records(sync_mode="full_refresh"))

        call_args = mock_get.call_args
        assert "https://studio.biggeo.com/data-sources/v1/get-data-source/my_data_source" in call_args[0][0]
