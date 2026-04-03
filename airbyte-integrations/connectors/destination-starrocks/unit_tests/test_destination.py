# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.exc import OperationalError

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)

from destination_starrocks.destination import DestinationStarRocks


logger = logging.getLogger("airbyte")


def _config(**kwargs):
    base = {"host": "testhost", "username": "admin", "password": "pass", "database": "testdb"}
    base.update(kwargs)
    return base


def _catalog(stream_name="users"):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={"properties": {"id": {"type": "integer"}}},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _mock_engine_success(mock_factory):
    """Wire up a mock engine that passes all check() assertions."""
    mock_conn = MagicMock()
    cm = MagicMock()
    cm.__enter__ = Mock(return_value=mock_conn)
    cm.__exit__ = Mock(return_value=False)
    mock_engine = MagicMock()
    mock_engine.connect.return_value = cm
    mock_factory.return_value = mock_engine

    select1 = Mock()
    select1.fetchone.return_value = (1,)
    mock_conn.execute.side_effect = [select1, Mock(), Mock()]


@patch("destination_starrocks.destination.StarRocksWriter")
@patch("destination_starrocks.destination.create_engine")
def test_check_succeeds(mock_factory, mock_writer_cls):
    _mock_engine_success(mock_factory)
    mock_writer = MagicMock()
    mock_writer.verify_stream_load_connectivity.return_value = True
    mock_writer._stream_load_base_url = "http://testhost:8030"
    mock_writer_cls.return_value = mock_writer

    result = DestinationStarRocks().check(logger, _config())
    assert result.status == Status.SUCCEEDED


@patch("destination_starrocks.destination.create_engine")
def test_check_fails_on_auth_error(mock_factory):
    mock_engine = MagicMock()
    mock_factory.return_value = mock_engine
    cm = MagicMock()
    cm.__enter__.side_effect = OperationalError("SELECT 1", {}, Exception("Access denied"))
    cm.__exit__ = Mock(return_value=False)
    mock_engine.connect.return_value = cm

    result = DestinationStarRocks().check(logger, _config())
    assert result.status == Status.FAILED
    assert "authentication" in result.message.lower()


@patch("destination_starrocks.destination.StarRocksWriter")
@patch("destination_starrocks.destination.create_engine")
def test_check_fails_when_stream_load_inaccessible(mock_factory, mock_writer_cls):
    _mock_engine_success(mock_factory)
    mock_writer = MagicMock()
    mock_writer.verify_stream_load_connectivity.return_value = False
    mock_writer._stream_load_base_url = "http://testhost:8030"
    mock_writer_cls.return_value = mock_writer

    result = DestinationStarRocks().check(logger, _config())
    assert result.status == Status.FAILED
    assert "Stream Load" in result.message


def test_check_fails_on_invalid_config():
    result = DestinationStarRocks().check(logger, {"host": "h"})  # missing username + database
    assert result.status == Status.FAILED


@patch("destination_starrocks.destination.StarRocksWriter")
def test_write_uses_typed_mode_by_default(mock_writer_cls):
    mock_writer = MagicMock()
    mock_writer.write_typed.return_value = iter([])
    mock_writer_cls.return_value = mock_writer

    list(DestinationStarRocks().write(_config(), _catalog(), iter([])))
    mock_writer.write_typed.assert_called_once()
    mock_writer.write_raw.assert_not_called()


@patch("destination_starrocks.destination.StarRocksWriter")
def test_write_uses_raw_mode(mock_writer_cls):
    mock_writer = MagicMock()
    mock_writer.write_raw.return_value = iter([])
    mock_writer_cls.return_value = mock_writer

    list(DestinationStarRocks().write(_config(loading_mode={"mode": "raw"}), _catalog(), iter([])))
    mock_writer.write_raw.assert_called_once()
    mock_writer.write_typed.assert_not_called()


@patch("destination_starrocks.destination.StarRocksWriter")
def test_write_yields_state_messages(mock_writer_cls):
    state_msg = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"cursor": 99}))
    mock_writer = MagicMock()
    mock_writer.write_typed.return_value = iter([state_msg])
    mock_writer_cls.return_value = mock_writer

    output = list(DestinationStarRocks().write(_config(), _catalog(), iter([])))
    assert len(output) == 1
    assert output[0].type == Type.STATE
