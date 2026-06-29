# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, Mock, patch

import pytest

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)

from destination_starrocks.config import StarRocksConfig
from destination_starrocks.writer import StarRocksWriter


def _config(**kwargs) -> StarRocksConfig:
    base = {"host": "testhost", "username": "admin", "database": "testdb"}
    base.update(kwargs)
    return StarRocksConfig(**base)


def _record(stream="users", data=None):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data=data or {"id": 1}, emitted_at=0),
    )


def _state():
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"cursor": 1}))


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


def _make_writer(config=None):
    if config is None:
        config = _config()

    mock_conn = MagicMock()
    mock_engine = MagicMock()
    cm = MagicMock()
    cm.__enter__ = Mock(return_value=mock_conn)
    cm.__exit__ = Mock(return_value=False)
    mock_engine.connect.return_value = cm

    with patch("destination_starrocks.writer.create_engine", return_value=mock_engine), \
         patch("destination_starrocks.writer.requests.Session"):
        writer = StarRocksWriter(config)

    mock_session = MagicMock()
    success = Mock()
    success.status_code = 200
    success.json.return_value = {"Status": "Success", "NumberLoadedRows": 1}
    mock_session.put.return_value = success
    mock_session.get.return_value = Mock(status_code=200)
    writer.session = mock_session
    writer.engine = mock_engine

    return writer, mock_session


def test_http_vs_https_url():
    http_writer, _ = _make_writer(_config(http_port=8030, ssl=False))
    https_writer, _ = _make_writer(_config(http_port=443, ssl=True))
    assert http_writer._stream_load_base_url == "http://testhost:8030"
    assert https_writer._stream_load_base_url == "https://testhost:443"


def test_write_skips_unknown_stream():
    writer, mock_session = _make_writer()
    list(writer.write_raw(_catalog("users"), iter([_record("no_such_stream")] * 5)))
    mock_session.put.assert_not_called()


def test_state_triggers_flush_and_is_yielded():
    writer, mock_session = _make_writer()
    messages = [_record(), _state()]
    output = list(writer.write_raw(_catalog(), iter(messages)))
    mock_session.put.assert_called_once()
    states = [m for m in output if m.type == Type.STATE]
    assert len(states) == 1


def test_stream_load_raises_on_non_success_response():
    writer, mock_session = _make_writer()
    bad = Mock()
    bad.status_code = 200
    bad.json.return_value = {"Status": "Fail", "Message": "label already exists"}
    mock_session.put.return_value = bad

    with pytest.raises(Exception):
        writer._execute_raw_stream_load("users", "data\n", 1)


def test_sparse_columns_do_not_raise():
    writer, mock_session = _make_writer()
    writer._stream_columns["passengers"] = ["id", "name", "deck", "_airbyte_ab_id", "_airbyte_emitted_at"]
    writer._stream_col_types["passengers"] = {"id": "BIGINT", "name": "STRING", "deck": "STRING", "_airbyte_ab_id": "VARCHAR", "_airbyte_emitted_at": "DATETIME"}
    buffer = {
        "passengers": [
            {"id": 1, "name": "Alice", "_airbyte_ab_id": "u1", "_airbyte_emitted_at": "ts"},
            {"id": 2, "deck": "A", "_airbyte_ab_id": "u2", "_airbyte_emitted_at": "ts"},
        ]
    }
    writer._flush_typed_buffer_stream_load(buffer)
    mock_session.put.assert_called_once()
