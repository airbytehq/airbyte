#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock, patch

import pytest
from source_microsoft_sharepoint.source import SourceMicrosoftSharePoint
from source_microsoft_sharepoint.stream_reader import (
    SourceMicrosoftSharePointStreamReader,
)

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError


@pytest.fixture
def mock_logger():
    return logging.getLogger("airbyte.test")


@pytest.fixture
def mock_config():
    return {
        "credentials": {
            "auth_type": "Client",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "tenant_id": "test_tenant_id"
        },
        "site_url": "https://example.sharepoint.com/sites/test",
        "streams": [
            {
                "name": "test_stream",
                "globs": ["*.csv"],
                "validation_policy": "Emit Record",
                "format": {"filetype": "csv"}
            }
        ],
        "start_date": "2021-01-01T00:00:00Z",
        "folder_path": "Shared Documents"
    }


def test_check_connection_marks_stream_reader(mock_logger, mock_config):
    """
    Test that the mark_as_check method is called during check_connection.
    """
    # Create mock stream reader
    mock_stream_reader = MagicMock(spec=SourceMicrosoftSharePointStreamReader)
    
    # Create a source instance with the mock stream reader
    source = SourceMicrosoftSharePoint(None, None, None)
    source.stream_reader = mock_stream_reader
    
    # Patch parent check_connection method
    with patch(
        'source_microsoft_sharepoint.source.FileBasedSource.check_connection',
        return_value=(True, None)
    ):
        # Call check_connection directly
        source.check_connection(mock_logger, mock_config)
    
    # Verify mark_as_check was called
    mock_stream_reader.mark_as_check.assert_called_once()


@patch('source_microsoft_sharepoint.source.FileBasedSource.check_connection')
def test_check_connection_forwards_to_parent(
    mock_parent_check, mock_logger, mock_config
):
    """
    Test that check_connection forwards the call to the parent class after 
    marking the reader.
    """
    # Create a source instance
    source = SourceMicrosoftSharePoint(None, None, None)
    
    # Mock the parent check_connection to return a specific result
    mock_parent_check.return_value = (True, None)
    
    # Call check_connection
    result = source.check_connection(mock_logger, mock_config)
    
    # Verify parent method was called with correct arguments
    mock_parent_check.assert_called_once_with(mock_logger, mock_config)
    
    # Verify result is forwarded from parent
    assert result == (True, None)


@patch('source_microsoft_sharepoint.source.FileBasedSource.check_connection')
def test_check_connection_handles_exceptions(
    mock_parent_check, mock_logger, mock_config
):
    """Test that check_connection handles exceptions properly."""
    # Create a source instance
    source = SourceMicrosoftSharePoint(None, None, None)
    
    # Mock parent method to raise an exception
    mock_exception = AirbyteTracedException(
        message=FileBasedSourceError.CONFIG_VALIDATION_ERROR.value
    )
    mock_parent_check.side_effect = mock_exception
    
    # Call check_connection
    result = source.check_connection(mock_logger, mock_config)
    
    # Verify error is handled and returned properly
    assert result == (False, str(mock_exception)) 