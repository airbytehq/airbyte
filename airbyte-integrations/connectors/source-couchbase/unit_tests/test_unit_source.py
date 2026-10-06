#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_couchbase.source import SourceCouchbase
from source_couchbase.streams import DocumentStream


@pytest.fixture
def config():
    return {"connection_string": "couchbase://localhost", "username": "user", "password": "password", "bucket": "travel-sample"}


def test_set_config_values(config):
    source = SourceCouchbase()
    source._set_config_values(config)

    assert source.connection_string == config["connection_string"]
    assert source.username == config["username"]
    assert source.password == config["password"]
    assert source.bucket_name == config["bucket"]


def test_check_connection(mocker, config):
    source = SourceCouchbase()
    logger_mock = MagicMock()

    with patch.object(SourceCouchbase, "_set_config_values") as mock_set_config:
        with patch.object(SourceCouchbase, "_get_cluster") as mock_get_cluster:
            mock_cluster = MagicMock()
            mock_bucket = MagicMock()
            mock_get_cluster.return_value = mock_cluster
            mock_cluster.bucket.return_value = mock_bucket

            is_connected, error = source.check_connection(logger_mock, config)

            assert is_connected is True, "Connection check failed"
            assert error is None
            mock_set_config.assert_called_once_with(config)
            mock_get_cluster.assert_called_once()
            mock_cluster.bucket.assert_called_once_with(source.bucket_name)
            mock_bucket.ping.assert_called_once()


def test_check_connection_failure(mocker, config):
    source = SourceCouchbase()
    logger_mock = MagicMock()

    with patch.object(SourceCouchbase, "_set_config_values"):
        with patch.object(SourceCouchbase, "_get_cluster", side_effect=Exception("Connection failed")):
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

    with patch.object(SourceCouchbase, "_set_config_values") as mock_set_config:
        with patch.object(SourceCouchbase, "_get_cluster", return_value=mock_cluster):
            with patch.object(SourceCouchbase, "_ensure_primary_index") as mock_ensure_index:
                streams = source.streams(config)

                assert len(streams) == 1, "Expected one stream"
                assert isinstance(streams[0], DocumentStream), "Stream is not an instance of DocumentStream"
                assert streams[0].name == f"{source.bucket_name}.inventory.hotel", "Stream name is incorrect"

                mock_set_config.assert_called_once_with(config)
                mock_ensure_index.assert_called_once_with(mock_cluster, source.bucket_name, "inventory", "hotel")


def test_get_cluster(mocker, config):
    source = SourceCouchbase()
    source._set_config_values(config)

    with patch("source_couchbase.source.Cluster") as mock_cluster:
        with patch("source_couchbase.source.PasswordAuthenticator") as mock_auth:
            with patch("source_couchbase.source.ClusterOptions") as mock_options:
                cluster = source._get_cluster()

                mock_auth.assert_called_once_with(config["username"], config["password"])
                mock_options.assert_called_once_with(mock_auth.return_value)
                mock_cluster.assert_called_once_with(config["connection_string"], mock_options.return_value)
                assert cluster == mock_cluster.return_value


def test_ensure_primary_index(mocker, config):
    source = SourceCouchbase()
    mock_cluster = MagicMock()

    # Test when index doesn't exist
    mock_cluster.query.return_value.execute.return_value = None
    SourceCouchbase._ensure_primary_index(mock_cluster, "travel-sample", "inventory", "hotel")
    assert mock_cluster.query.call_count == 1, "Query should be called once"

    # Test when index already exists
    mock_cluster.query.reset_mock()
    mock_cluster.query.return_value.execute.side_effect = Exception("Index already exists")
    SourceCouchbase._ensure_primary_index(mock_cluster, "travel-sample", "inventory", "hotel")
    assert mock_cluster.query.call_count == 1, "Query should be called once"
