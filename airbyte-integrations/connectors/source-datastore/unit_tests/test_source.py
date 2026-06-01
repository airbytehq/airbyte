#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from google.cloud import datastore
from source_datastore.source import SourceDatastore
from source_datastore.streams import DatastoreStream


FAKE_CREDS = {
    "type": "service_account",
    "project_id": "my-project",
    "private_key_id": "key123",
    "private_key": (
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2a2rwplBQLF29amygykEMmYz0+Oe9Dp9cPNW1VpHrHFiM/3H\n-----END RSA PRIVATE KEY-----\n"
    ),
    "client_email": "sa@my-project.iam.gserviceaccount.com",
    "client_id": "123456",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}

CONFIG = {
    "project_id": "my-project",
    "credentials_json": json.dumps(FAKE_CREDS),
    "kinds": ["Product", "Order"],
    "namespace": "prod",
}

CONFIG_MINIMAL = {
    "project_id": "my-project",
    "credentials_json": json.dumps(FAKE_CREDS),
    "kinds": ["Product"],
}


@pytest.fixture
def mock_client():
    mock_query = MagicMock()
    mock_query.fetch.return_value = []
    client = MagicMock(spec=datastore.Client)
    client.query.return_value = mock_query
    return client


def test_streams_returns_one_stream_per_kind(mock_client):
    source = SourceDatastore()
    with patch("source_datastore.source._build_client", return_value=mock_client):
        streams = source.streams(CONFIG)
    assert len(streams) == 2
    assert all(isinstance(s, DatastoreStream) for s in streams)
    assert {s.name for s in streams} == {"product", "order"}


def test_streams_minimal_config(mock_client):
    source = SourceDatastore()
    with patch("source_datastore.source._build_client", return_value=mock_client):
        streams = source.streams(CONFIG_MINIMAL)
    assert len(streams) == 1
    assert streams[0].name == "product"


def test_streams_namespace_propagated(mock_client):
    source = SourceDatastore()
    with patch("source_datastore.source._build_client", return_value=mock_client):
        streams = source.streams(CONFIG)
    assert all(s._namespace == "prod" for s in streams)


def test_streams_no_cursor_field_on_stream(mock_client):
    """Cursor is user-defined in Airbyte UI, not set at source level."""
    source = SourceDatastore()
    with patch("source_datastore.source._build_client", return_value=mock_client):
        streams = source.streams(CONFIG)
    assert all(s._active_cursor is None for s in streams)


def test_check_connection_success(mock_client):
    source = SourceDatastore()
    with patch("source_datastore.source._build_client", return_value=mock_client):
        ok, error = source.check_connection(logging.getLogger(), CONFIG)
    assert ok is True
    assert error is None


def test_check_connection_no_kinds():
    source = SourceDatastore()
    config = {**CONFIG, "kinds": []}
    mock_client = MagicMock()
    with patch("source_datastore.source._build_client", return_value=mock_client):
        ok, error = source.check_connection(logging.getLogger(), config)
    assert ok is False
    assert "Kind" in error


def test_check_connection_client_error():
    source = SourceDatastore()
    with patch("source_datastore.source._build_client", side_effect=Exception("auth failed")):
        ok, error = source.check_connection(logging.getLogger(), CONFIG)
    assert ok is False
    assert "auth failed" in error
