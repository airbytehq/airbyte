# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for BigGeo source connector with chunked pagination support."""

from unittest.mock import MagicMock, call, patch

import pytest
from source_biggeo.source import DEFAULT_CHUNK_SIZE, BigGeoStream, SourceBiggeo


@pytest.fixture
def valid_config():
    return {
        "api_key": "test-api-key",
        "data_source_name": "test_data_source",
    }


@pytest.fixture
def valid_config_with_chunk_size():
    return {
        "api_key": "test-api-key",
        "data_source_name": "test_data_source",
        "chunk_size": 500,
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


# ============================================================================
# Connection Check Tests
# ============================================================================


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


# ============================================================================
# Stream Creation Tests
# ============================================================================


def test_streams_with_data_source_name(source, valid_config):
    """Test that streams are created when data_source_name is provided."""
    streams = source.streams(config=valid_config)

    assert len(streams) == 1
    assert streams[0].name == "test_data_source"
    assert isinstance(streams[0], BigGeoStream)
    assert streams[0].chunk_size == DEFAULT_CHUNK_SIZE


def test_streams_with_custom_chunk_size(source, valid_config_with_chunk_size):
    """Test that streams use custom chunk_size when provided."""
    streams = source.streams(config=valid_config_with_chunk_size)

    assert len(streams) == 1
    assert streams[0].chunk_size == 500


def test_streams_without_data_source_name(source):
    """Test that no streams are created when data_source_name is not provided."""
    config = {"api_key": "test-api-key"}
    streams = source.streams(config=config)

    assert len(streams) == 0


# ============================================================================
# BigGeoStream Basic Tests
# ============================================================================


def test_biggeo_stream_name():
    """Test that BigGeoStream returns correct name."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    assert stream.name == "my_data_source"


def test_biggeo_stream_default_chunk_size():
    """Test that BigGeoStream uses default chunk size."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    assert stream.chunk_size == DEFAULT_CHUNK_SIZE


def test_biggeo_stream_custom_chunk_size():
    """Test that BigGeoStream uses custom chunk size."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source", chunk_size=500)

    assert stream.chunk_size == 500


def test_biggeo_stream_headers():
    """Test that BigGeoStream returns correct headers."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    headers = stream._get_headers()

    assert headers["Content-Type"] == "application/json"
    assert headers["x-api-key"] == "test-key"


def test_biggeo_stream_get_json_schema():
    """Test that get_json_schema returns a flexible schema."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    schema = stream.get_json_schema()

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is True


# ============================================================================
# Chunked Pagination Tests
# ============================================================================


def test_biggeo_stream_read_records_single_chunk():
    """Test reading records when all data fits in a single chunk (hasMore=False)."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test", chunk_size=1000)

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": 1, "name": "record1"},
                {"id": 2, "name": "record2"},
            ],
            "syncId": "sync-123",
            "nextCursor": None,
            "hasMore": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        records = list(stream.read_records(sync_mode="full_refresh"))

        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[1]["id"] == 2
        mock_get.assert_called_once()

        # Verify query params
        call_args = mock_get.call_args
        assert call_args.kwargs["params"]["chunkSize"] == "1000"
        assert "cursor" not in call_args.kwargs["params"]
        assert "syncId" not in call_args.kwargs["params"]


def test_biggeo_stream_read_records_multiple_chunks():
    """Test reading records across multiple chunks with pagination."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test", chunk_size=2)

    with patch("requests.get") as mock_get:
        # First chunk response
        first_response = MagicMock()
        first_response.json.return_value = {
            "data": [{"id": 1}, {"id": 2}],
            "syncId": "sync-abc",
            "nextCursor": 2,
            "hasMore": True,
        }
        first_response.raise_for_status.return_value = None

        # Second chunk response
        second_response = MagicMock()
        second_response.json.return_value = {
            "data": [{"id": 3}, {"id": 4}],
            "syncId": "sync-abc",
            "nextCursor": 4,
            "hasMore": True,
        }
        second_response.raise_for_status.return_value = None

        # Final chunk response
        third_response = MagicMock()
        third_response.json.return_value = {
            "data": [{"id": 5}],
            "syncId": "sync-abc",
            "nextCursor": None,
            "hasMore": False,
        }
        third_response.raise_for_status.return_value = None

        mock_get.side_effect = [first_response, second_response, third_response]

        records = list(stream.read_records(sync_mode="full_refresh"))

        assert len(records) == 5
        assert [r["id"] for r in records] == [1, 2, 3, 4, 5]
        assert mock_get.call_count == 3


def test_biggeo_stream_pagination_params():
    """Test that correct pagination params are sent in subsequent requests."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test", chunk_size=100)

    with patch("requests.get") as mock_get:
        # First chunk
        first_response = MagicMock()
        first_response.json.return_value = {
            "data": [{"id": 1}],
            "syncId": "sync-xyz",
            "nextCursor": 100,
            "hasMore": True,
        }
        first_response.raise_for_status.return_value = None

        # Second chunk (final)
        second_response = MagicMock()
        second_response.json.return_value = {
            "data": [{"id": 2}],
            "syncId": "sync-xyz",
            "nextCursor": None,
            "hasMore": False,
        }
        second_response.raise_for_status.return_value = None

        mock_get.side_effect = [first_response, second_response]

        list(stream.read_records(sync_mode="full_refresh"))

        # Check first call - no cursor or syncId
        first_call = mock_get.call_args_list[0]
        assert first_call.kwargs["params"]["chunkSize"] == "100"
        assert "cursor" not in first_call.kwargs["params"]
        assert "syncId" not in first_call.kwargs["params"]

        # Check second call - includes cursor and syncId
        second_call = mock_get.call_args_list[1]
        assert second_call.kwargs["params"]["chunkSize"] == "100"
        assert second_call.kwargs["params"]["cursor"] == "100"
        assert second_call.kwargs["params"]["syncId"] == "sync-xyz"


def test_biggeo_stream_empty_response():
    """Test handling of empty data response."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "syncId": "sync-empty",
            "nextCursor": None,
            "hasMore": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        records = list(stream.read_records(sync_mode="full_refresh"))

        assert len(records) == 0
        mock_get.assert_called_once()


def test_biggeo_stream_handles_missing_data_key():
    """Test that missing data key in response defaults to empty list."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "syncId": "sync-123",
            "nextCursor": None,
            "hasMore": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        records = list(stream.read_records(sync_mode="full_refresh"))

        assert len(records) == 0


def test_biggeo_stream_safety_stop_on_none_cursor():
    """Test that pagination stops if hasMore=True but nextCursor is None."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        # First chunk with hasMore=True but nextCursor=None (edge case)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": 1}],
            "syncId": "sync-123",
            "nextCursor": None,
            "hasMore": True,  # Inconsistent state
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        records = list(stream.read_records(sync_mode="full_refresh"))

        # Should stop after first chunk due to safety check
        assert len(records) == 1
        mock_get.assert_called_once()


def test_biggeo_stream_url_construction():
    """Test that the correct URL is constructed with query params."""
    stream = BigGeoStream(api_key="test-key", data_source_name="my_data_source")

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [],
            "syncId": "sync-123",
            "nextCursor": None,
            "hasMore": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        list(stream.read_records(sync_mode="full_refresh"))

        call_args = mock_get.call_args
        assert "https://studio.biggeo.com/data-sources/v1/get-data-source/my_data_source" in call_args[0][0]


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_biggeo_stream_request_exception():
    """Test that request exceptions are properly raised."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection failed")

        with pytest.raises(Exception) as exc_info:
            list(stream.read_records(sync_mode="full_refresh"))

        assert "Connection failed" in str(exc_info.value)


def test_biggeo_stream_http_error():
    """Test handling of HTTP errors from the API."""
    stream = BigGeoStream(api_key="test-key", data_source_name="test")

    with patch("requests.get") as mock_get:
        import requests

        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        with pytest.raises(requests.exceptions.RequestException):
            list(stream.read_records(sync_mode="full_refresh"))
