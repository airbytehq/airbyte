# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Integration tests for BigGeo destination connector."""

import json
from logging import getLogger
from pathlib import Path

import pytest
from destination_biggeo.destination import DestinationBiggeo

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


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
        return {"api_key": "invalid-key-12345", "batch_size": 1000}


@pytest.fixture
def destination():
    """Create a DestinationBiggeo instance"""
    return DestinationBiggeo()


@pytest.fixture
def configured_catalog():
    """Create a simple configured catalog for testing"""
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="test_stream",
            json_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "timestamp": {"type": "string"},
                },
            },
            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[stream])


def test_check_connection_success(destination, config):
    """Test that check succeeds with valid API key."""
    if config.get("api_key") == "your-api-key-here":
        pytest.skip("Skipping test - please provide a valid API key in integration_tests/config.json")

    status = destination.check(logger=logger, config=config)

    assert status.status == Status.SUCCEEDED, f"Check failed with message: {status.message}"


def test_check_connection_failure(destination, invalid_config):
    """Test that check fails with invalid API key."""
    status = destination.check(logger=logger, config=invalid_config)

    assert status.status == Status.FAILED
    assert status.message is not None


def test_check_connection_missing_api_key(destination):
    """Test that check fails when API key is missing."""
    empty_config = {}
    status = destination.check(logger=logger, config=empty_config)

    assert status.status == Status.FAILED
    assert "API Key is required" in status.message


def test_write_single_record(destination, config, configured_catalog):
    """Test writing a single record to BigGeo."""
    if config.get("api_key") == "your-api-key-here":
        pytest.skip("Skipping test - please provide a valid API key in integration_tests/config.json")

    messages = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_stream",
                data={"id": 1, "name": "test_record", "timestamp": "2024-01-01T00:00:00Z"},
                emitted_at=1609459200000,
            ),
        ),
    ]

    output_messages = list(destination.write(config, configured_catalog, messages))

    assert output_messages is not None


def test_write_multiple_records(destination, config, configured_catalog):
    """Test writing multiple records to BigGeo."""

    if config.get("api_key") == "your-api-key-here":
        pytest.skip("Skipping test - please provide a valid API key in integration_tests/config.json")

    messages = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_stream",
                data={"id": i, "name": f"test_record_{i}", "timestamp": f"2024-01-{i:02d}T00:00:00Z"},
                emitted_at=1609459200000 + (i * 1000),
            ),
        )
        for i in range(1, 11)
    ]

    output_messages = list(destination.write(config, configured_catalog, messages))

    assert output_messages is not None


def test_write_with_state_messages(destination, config, configured_catalog):
    """Test writing records with state messages."""
    if config.get("api_key") == "your-api-key-here":
        pytest.skip("Skipping test - please provide a valid API key in integration_tests/config.json")

    messages = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_stream",
                data={"id": 1, "name": "test_record_1", "timestamp": "2024-01-01T00:00:00Z"},
                emitted_at=1609459200000,
            ),
        ),
        AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(data={"last_id": 1}),
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_stream",
                data={"id": 2, "name": "test_record_2", "timestamp": "2024-01-02T00:00:00Z"},
                emitted_at=1609459201000,
            ),
        ),
        AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(data={"last_id": 2}),
        ),
    ]

    output_messages = list(destination.write(config, configured_catalog, messages))

    state_messages = [msg for msg in output_messages if msg.type == Type.STATE]
    assert len(state_messages) == 2


def test_write_empty_stream(destination, config, configured_catalog):
    """Test writing an empty stream."""
    if config.get("api_key") == "your-api-key-here":
        pytest.skip("Skipping test - please provide a valid API key in integration_tests/config.json")

    messages = []

    output_messages = list(destination.write(config, configured_catalog, messages))

    assert output_messages == []


@pytest.mark.parametrize("batch_size", [1, 5, 100])
def test_write_with_different_batch_sizes(destination, config, configured_catalog, batch_size):
    """Test writing with different batch sizes."""
    if config.get("api_key") == "your-api-key-here":
        pytest.skip("Skipping test - please provide a valid API key in integration_tests/config.json")

    test_config = {**config, "batch_size": batch_size}

    messages = [
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream="test_stream",
                data={"id": i, "name": f"test_record_{i}", "timestamp": f"2024-01-{i:02d}T00:00:00Z"},
                emitted_at=1609459200000 + (i * 1000),
            ),
        )
        for i in range(1, 21)
    ]

    output_messages = list(destination.write(test_config, configured_catalog, messages))

    assert output_messages is not None
