#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_couchbase.source import SourceCouchbase
from source_couchbase.streams import Buckets, Scopes, Collections, Documents

@pytest.fixture
def config():
    return {
        "connection_string": "couchbase://localhost",
        "username": "user",
        "password": "password"
    }

def test_check_connection(mocker, config):
    source = SourceCouchbase()
    logger_mock = MagicMock()
    
    with patch("source_couchbase.source.Cluster") as mock_cluster:
        mock_cluster_instance = mock_cluster.return_value
        mock_cluster_instance.ping.return_value = None
        
        is_connected, error = source.check_connection(logger_mock, config)
        
        assert is_connected is True
        assert error is None
        mock_cluster.assert_called_once_with(config['connection_string'], mocker.ANY)
        mock_cluster_instance.ping.assert_called_once()

def test_check_connection_failure(mocker, config):
    source = SourceCouchbase()
    logger_mock = MagicMock()
    
    with patch("source_couchbase.source.Cluster") as mock_cluster:
        mock_cluster.side_effect = Exception("Connection failed")
        
        is_connected, error = source.check_connection(logger_mock, config)
        
        assert is_connected is False
        assert "Connection check failed" in str(error)

def test_streams(mocker, config):
    source = SourceCouchbase()
    
    with patch("source_couchbase.source.Cluster") as mock_cluster:
        streams = source.streams(config)
        
        assert len(streams) == 4
        assert any(isinstance(stream, Buckets) for stream in streams)
        assert any(isinstance(stream, Scopes) for stream in streams)
        assert any(isinstance(stream, Collections) for stream in streams)
        assert any(isinstance(stream, Documents) for stream in streams)

        mock_cluster.assert_called_once_with(config['connection_string'], mocker.ANY)
