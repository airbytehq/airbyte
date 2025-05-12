#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import datetime
import logging
from typing import Any, Dict, List, Mapping

import pytest
from destination_sftp import DestinationSftp
from destination_sftp.client import SftpClient

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


@pytest.fixture
def csv_config(config) -> Dict[str, Any]:
    """Fixture for configuration with CSV format"""
    return {**config, "file_format": "csv"}


@pytest.fixture
def custom_naming_config(config) -> Dict[str, Any]:
    """Fixture for configuration with custom naming pattern"""
    return {**config, "file_name_pattern": "{stream}_data"}


@pytest.fixture
def directory_config(config) -> Dict[str, Any]:
    """Fixture for configuration with directory organization"""
    return {**config, "file_name_pattern": "test/{stream}"}


@pytest.fixture
def ssh_algorithm_config(config) -> Dict[str, Any]:
    """Fixture for configuration with SSH algorithms"""
    return {**config, "ssh_algorithms": {"server_host_key": ["ssh-rsa", "ecdsa-sha2-nistp256"]}}


@pytest.fixture
def csv_client(csv_config) -> SftpClient:
    """Fixture for a CSV-configured client"""
    with SftpClient(**csv_config) as client:
        yield client
        # Clean up files created during tests
        try:
            client.delete("test_stream")
        except:
            pass


@pytest.fixture
def custom_naming_client(custom_naming_config) -> SftpClient:
    """Fixture for a client with custom naming pattern"""
    with SftpClient(**custom_naming_config) as client:
        yield client
        # Clean up files created during tests
        try:
            client.delete("test_stream")
        except:
            pass


@pytest.fixture
def directory_client(directory_config) -> SftpClient:
    """Fixture for a client with directory organization"""
    with SftpClient(**directory_config) as client:
        yield client
        # Clean up files created during tests
        try:
            client.delete("test_stream")
        except:
            pass


def test_csv_format(csv_client):
    """Test that CSV format works correctly"""
    # Write test data
    csv_client.write("test_stream", {"col1": "value1", "col2": 123})
    csv_client.write("test_stream", {"col1": "value2", "col2": 456})

    # Read it back
    data = csv_client.read_data("test_stream")

    # Verify data was correctly formatted as CSV
    assert len(data) == 2
    assert data[0]["col1"] == "value1"
    assert data[0]["col2"] == "123"  # Note: CSV reads numbers as strings
    assert data[1]["col1"] == "value2"
    assert data[1]["col2"] == "456"

    # Verify path format
    assert csv_client._get_path("test_stream").endswith(".csv")
    assert "airbyte_csv_test_stream.csv" in csv_client._get_path("test_stream")


def test_custom_naming(custom_naming_client):
    """Test that custom naming patterns work correctly"""
    # Write test data
    custom_naming_client.write("test_stream", {"field": "test_value"})

    # Verify path format
    assert "test_stream_data.jsonl" in custom_naming_client._get_path("test_stream")

    # Read it back to verify it works
    data = custom_naming_client.read_data("test_stream")
    assert len(data) == 1
    assert data[0]["field"] == "test_value"


def test_directory_organization(directory_client):
    """Test that directory organization works correctly"""
    # Write test data
    directory_client.write("test_stream", {"field": "test_value"})

    # Verify path format includes directory
    path = directory_client._get_path("test_stream")
    assert "test/test_stream.jsonl" in path

    # Read it back to verify it works
    data = directory_client.read_data("test_stream")
    assert len(data) == 1
    assert data[0]["field"] == "test_value"


def test_ssh_algorithm_connection(ssh_algorithm_config):
    """Test that SSH algorithm configuration doesn't break connection"""
    # Just test that the connection succeeds
    outcome = DestinationSftp().check(logging.getLogger("airbyte-destination"), ssh_algorithm_config)
    assert outcome.status == Status.SUCCEEDED


def test_check_validates_new_parameters(config):
    """Test that invalid configurations for new parameters are caught"""
    # Test invalid file format
    invalid_format_config = {**config, "file_format": "invalid"}
    outcome = DestinationSftp().check(logging.getLogger("airbyte-destination"), invalid_format_config)
    assert outcome.status == Status.FAILED

    # Test invalid file pattern with missing required variables
    invalid_pattern_config = {**config, "file_name_pattern": "static_name_without_variables"}
    # This should still succeed since we don't validate the pattern structure
    outcome = DestinationSftp().check(logging.getLogger("airbyte-destination"), invalid_pattern_config)
    assert outcome.status == Status.SUCCEEDED
