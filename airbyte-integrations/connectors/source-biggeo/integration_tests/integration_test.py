# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Integration tests for BigGeo source connector."""

import json
from logging import getLogger
from pathlib import Path

import pytest
from source_biggeo.source import SourceBiggeo


logger = getLogger("airbyte")


@pytest.fixture
def config():
    """Load config from integration_tests/config.json"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r") as f:
        return json.load(f)


@pytest.fixture
def invalid_config():
    """Load invalid config for failure testing"""
    invalid_config_path = Path(__file__).parent / "invalid_config.json"
    if invalid_config_path.exists():
        with open(invalid_config_path, "r") as f:
            return json.load(f)
    else:
        # Return config with invalid API key
        return {"api_key": "invalid-key-12345", "data_source_name": "test_data_source"}


@pytest.fixture
def source():
    """Create a SourceBiggeo instance"""
    return SourceBiggeo()


def test_check_connection_success(source, config):
    """Test that check succeeds with valid API key."""
    success, message = source.check_connection(logger=logger, config=config)

    assert success is True, f"Check failed with message: {message}"


def test_check_connection_failure(source, invalid_config):
    """Test that check fails with invalid API key."""
    success, message = source.check_connection(logger=logger, config=invalid_config)

    assert success is False
    assert message is not None


def test_check_connection_missing_api_key(source):
    """Test that check fails when API key is missing."""
    empty_config = {"data_source_name": "test"}
    success, message = source.check_connection(logger=logger, config=empty_config)

    assert success is False
    assert "API Key is required" in message


def test_streams_creation(source, config):
    """Test that streams are created correctly."""
    streams = source.streams(config=config)

    assert len(streams) > 0
    assert streams[0].name == config.get("data_source_name")


def test_read_records(source, config):
    """Test reading records from BigGeo."""
    streams = source.streams(config=config)

    if len(streams) == 0:
        pytest.fail("No streams available - data_source_name may not be configured")

    stream = streams[0]

    # Try to read records from the stream
    records = []
    try:
        for record_slice in stream.read_records(sync_mode="full_refresh"):
            records.append(record_slice)
    except Exception as e:
        error_msg = str(e)
        # Authentication errors should fail the test
        if "401" in error_msg or "Unauthorized" in error_msg or "API key validation failed" in error_msg:
            pytest.fail(f"Authentication failed - check your API key: {e}")
        # Other errors (like data source not found) are also failures
        pytest.fail(f"Failed to read records: {e}")

    # Successfully read records (could be empty list if data source is empty)
    assert isinstance(records, list)


def test_streams_without_data_source_name(source):
    """Test that no streams are created when data_source_name is not provided."""
    config = {"api_key": "test-api-key"}
    streams = source.streams(config=config)

    assert len(streams) == 0


def test_discover(source, config):
    """Test the discover command."""
    streams = source.streams(config=config)

    # Check that we can get the schema for each stream
    for stream in streams:
        schema = stream.get_json_schema()
        assert schema is not None
        assert "type" in schema
        assert schema["type"] == "object"


def test_connection_with_different_data_sources(source, config):
    """Test connecting to different data sources."""
    # Test with the configured data source
    streams = source.streams(config=config)
    assert len(streams) > 0

    # Test with a different data source name (may or may not exist)
    different_config = {**config, "data_source_name": "different_data_source"}
    streams = source.streams(config=different_config)
    assert len(streams) == 1
    assert streams[0].name == "different_data_source"
