#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_couchbase.source import SourceCouchbase
from source_couchbase.streams import CouchbaseStream, IncrementalCouchbaseStream

@pytest.fixture
def config():
    return {
        "connection_string": "couchbase://localhost",
        "username": "user",
        "password": "password",
        "bucket": "travel-sample"
    }

def test_check_connection(mocker, config):
    source = SourceCouchbase()
    logger_mock = MagicMock()
    
    with patch("source_couchbase.source.Cluster") as mock_cluster:
        mock_cluster_instance = mock_cluster.return_value
        mock_bucket = MagicMock()
        mock_cluster_instance.bucket.return_value = mock_bucket
        mock_bucket.ping.return_value = None
        
        is_connected, error = source.check_connection(logger_mock, config)
        
        assert is_connected is True, "Connection check failed"
        assert error is None
        mock_cluster.assert_called_once_with(config['connection_string'], mocker.ANY)
        mock_cluster_instance.bucket.assert_called_once_with(config['bucket'])
        mock_bucket.ping.assert_called_once()

def test_check_connection_failure(mocker, config):
    source = SourceCouchbase()
    logger_mock = MagicMock()
    
    with patch("source_couchbase.source.Cluster") as mock_cluster:
        mock_cluster.side_effect = Exception("Connection failed")
        
        is_connected, error = source.check_connection(logger_mock, config)
        
        assert is_connected is False, "Connection should fail"
        assert "Connection check failed" in str(error)

def test_streams(mocker, config):
    source = SourceCouchbase()
    
    mock_cluster = MagicMock()
    mock_bucket = MagicMock()
    mock_scope = MagicMock()
    mock_collection = MagicMock()

    mock_cluster.bucket.return_value = mock_bucket
    mock_bucket.collections.return_value.get_all_scopes.return_value = [mock_scope]
    mock_scope.collections = [mock_collection]
    mock_scope.name = "inventory"
    mock_collection.name = "hotel"

    with patch("source_couchbase.source.Cluster", return_value=mock_cluster):
        with patch.object(SourceCouchbase, "_ensure_primary_index") as mock_ensure_index:
            streams = source.streams(config)
        
            assert len(streams) == 1, "Expected one stream"
            assert isinstance(streams[0], CouchbaseStream), "Stream is not an instance of CouchbaseStream"
            assert streams[0].name == "travel-sample.inventory.hotel", "Stream name is incorrect"

            mock_ensure_index.assert_called_once_with(mock_cluster, "travel-sample", "inventory", "hotel")

def test_streams_incremental(mocker, config):
    config["use_incremental"] = True
    source = SourceCouchbase()
    
    mock_cluster = MagicMock()
    mock_bucket = MagicMock()
    mock_scope = MagicMock()
    mock_collection = MagicMock()

    mock_cluster.bucket.return_value = mock_bucket
    mock_bucket.collections.return_value.get_all_scopes.return_value = [mock_scope]
    mock_scope.collections = [mock_collection]
    mock_scope.name = "inventory"
    mock_collection.name = "hotel"

    with patch("source_couchbase.source.Cluster", return_value=mock_cluster):
        with patch.object(SourceCouchbase, "_ensure_primary_index") as mock_ensure_index:
            streams = source.streams(config)
        
            assert len(streams) == 1, "Expected one incremental stream"
            assert isinstance(streams[0], IncrementalCouchbaseStream), "Stream is not an instance of IncrementalCouchbaseStream"
            assert streams[0].name == "travel-sample.inventory.hotel", "Stream name is incorrect"
            assert streams[0].cursor_field == "_ab_cdc_updated_at", "Cursor field is incorrect"

            mock_ensure_index.assert_called_once_with(mock_cluster, "travel-sample", "inventory", "hotel")

def test_ensure_primary_index(mocker, config):
    source = SourceCouchbase()
    mock_cluster = MagicMock()

    # Test when index doesn't exist
    mock_cluster.query.return_value.execute.return_value = None
    source._ensure_primary_index(mock_cluster, "travel-sample", "inventory", "hotel")
    assert mock_cluster.query.call_count == 1, "Query should be called once"

    # Test when index already exists
    mock_cluster.query.reset_mock()
    mock_cluster.query.return_value.execute.side_effect = Exception("Index already exists")
    source._ensure_primary_index(mock_cluster, "travel-sample", "inventory", "hotel")
    assert mock_cluster.query.call_count == 1, "Query should be called once"

def test_validate_config(config):
    source = SourceCouchbase()
    
    # Test valid config
    is_valid, error = source._validate_config(config)
    assert is_valid is True, "Config should be valid"
    assert error is None

    # Test missing required field
    invalid_config = config.copy()
    del invalid_config["bucket"]
    is_valid, error = source._validate_config(invalid_config)
    assert is_valid is False, "Config should be invalid"
    assert "Missing required configuration fields" in error

    # Test incremental sync (no need to specify cursor field anymore)
    valid_incremental_config = config.copy()
    valid_incremental_config["use_incremental"] = True
    is_valid, error = source._validate_config(valid_incremental_config)
    assert is_valid is True, "Config should be valid"
    assert error is None
