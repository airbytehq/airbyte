#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from typing import Any, Dict
from unittest import mock
from unittest.mock import Mock

from destination_glassflow import DestinationGlassflow
from glassflow import errors

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


config = {"pipeline_id": "12345", "pipeline_access_token": "67890"}


def _init_mocks(client):
    pipeline = Mock()
    client.return_value = pipeline
    return pipeline


@mock.patch("destination_glassflow.destination.PipelineDataSource")
def test_check_succeeds(client):
    pipeline = _init_mocks(client)
    pipeline.validate_credentials.return_value = None
    destination = DestinationGlassflow()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.SUCCEEDED


@mock.patch("destination_glassflow.destination.PipelineDataSource")
def test_check_fails(client):
    pipeline = _init_mocks(client)
    pipeline.validate_credentials.side_effect = errors.PipelineAccessTokenInvalidError(mock.Mock())
    destination = DestinationGlassflow()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.FAILED


def _state() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={}))


def _record(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=0))


def _configured_catalog() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {}}
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="test", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@mock.patch("destination_glassflow.destination.PipelineDataSource")
def test_write_succeeds(client):
    stream = "test"
    data = {"field1": "test-value", "field2": "test-value"}
    emitted_at = 0
    pipeline = _init_mocks(client)
    input_messages = [_record(stream=stream, data=data), _state()]
    destination = DestinationGlassflow()
    for m in destination.write(config=config, configured_catalog=_configured_catalog(), input_messages=input_messages):
        assert m.type == Type.STATE

    _, (args,), _ = pipeline.publish.mock_calls[0]
    assert args["stream"] == stream
    assert args["data"] == data
    assert args["emitted_at"] == emitted_at
    pipeline.publish.assert_called()


@mock.patch("destination_glassflow.destination.PipelineDataSource")
def test_write_skips_message_from_unknown_stream(client):
    stream = "unknown_stream"
    data = {"field1": "test-value", "field2": "test-value"}
    pipeline = _init_mocks(client)
    input_messages = [_record(stream=stream, data=data), _state()]
    destination = DestinationGlassflow()
    for m in destination.write(config=config, configured_catalog=_configured_catalog(), input_messages=input_messages):
        assert m.type == Type.STATE
    pipeline.publish.assert_not_called()
