"""Unit tests for the SourceComfyUI connector class."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from source_comfyui.source import SourceComfyUI


@pytest.fixture
def config():
    return {
        "api_key": "test-api-key-123",
        "base_url": "https://cloud.comfy.org",
    }


@pytest.fixture
def source():
    return SourceComfyUI()


# ── check_connection ─────────────────────────────────────────────────────────


def test_check_connection_success(source, config):
    """Successful connection returns (True, None)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "system": {"os": "linux", "python_version": "3.11"},
        "devices": [],
    }
    mock_response.raise_for_status = MagicMock()

    with patch(
        "source_comfyui.source.requests.get", return_value=mock_response
    ) as mock_get:
        ok, error = source.check_connection(None, config)

        assert ok is True
        assert error is None
        mock_get.assert_called_once_with(
            "https://cloud.comfy.org/api/system_stats",
            headers={"X-API-Key": "test-api-key-123"},
            timeout=30,
        )


def test_check_connection_failure(source, config):
    """401 response returns (False, error_message)."""
    mock_response = MagicMock()
    mock_response.status_code = 401

    http_error = requests.exceptions.HTTPError(response=mock_response)
    mock_response.raise_for_status.side_effect = http_error

    with patch("source_comfyui.source.requests.get", return_value=mock_response):
        ok, error = source.check_connection(None, config)

        assert ok is False
        assert "Invalid API key" in error


def test_check_connection_forbidden(source, config):
    """403 response returns permission error."""
    mock_response = MagicMock()
    mock_response.status_code = 403

    http_error = requests.exceptions.HTTPError(response=mock_response)
    mock_response.raise_for_status.side_effect = http_error

    with patch("source_comfyui.source.requests.get", return_value=mock_response):
        ok, error = source.check_connection(None, config)

        assert ok is False
        assert "permissions" in error


def test_check_connection_timeout(source, config):
    """Timeout returns (False, descriptive error)."""
    with patch(
        "source_comfyui.source.requests.get",
        side_effect=requests.exceptions.Timeout(),
    ):
        ok, error = source.check_connection(None, config)

        assert ok is False
        assert "timed out" in error


def test_check_connection_unreachable(source, config):
    """Connection error returns (False, descriptive error)."""
    with patch(
        "source_comfyui.source.requests.get",
        side_effect=requests.exceptions.ConnectionError(),
    ):
        ok, error = source.check_connection(None, config)

        assert ok is False
        assert "Could not connect" in error


def test_check_connection_strips_trailing_slash(source):
    """Trailing slash on base_url is stripped before building the URL."""
    config = {"api_key": "key", "base_url": "https://example.com/"}
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()

    with patch(
        "source_comfyui.source.requests.get", return_value=mock_response
    ) as mock_get:
        source.check_connection(None, config)

        called_url = mock_get.call_args[0][0]
        assert called_url == "https://example.com/api/system_stats"


# ── streams ──────────────────────────────────────────────────────────────────


def test_streams_count(source, config):
    """streams() returns exactly 6 stream instances."""
    streams = source.streams(config)
    assert len(streams) == 6


def test_streams_uses_default_base_url(source):
    """When base_url is omitted, the default is used."""
    config = {"api_key": "key"}
    streams = source.streams(config)
    assert len(streams) == 6
