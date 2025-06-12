#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict
from unittest import mock
from unittest.mock import Mock

from destination_rabbitmq.destination import DestinationRabbitmq
from pika.spec import Queue

from airbyte_cdk.models import AirbyteMessage, Status, Type
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


config = {
    "host": "test.rabbitmq",
    "port": 5672,
    "virtual_host": "test_vh",
    "username": "john.doe",
    "password": "secret",
    "exchange": "test_exchange",
    "routing_key": "test_routing_key",
}


def _init_mocks(connection_init):
    connection, channel = Mock(), Mock()
    connection_init.return_value = connection
    connection.channel.return_value = channel
    return channel


@mock.patch("destination_rabbitmq.destination.BlockingConnection")
def test_check_succeeds(connection_init):
    result = Mock()
    result.method = Queue.DeclareOk()
    channel = _init_mocks(connection_init=connection_init)
    channel.queue_declare.return_value = result
    destination = DestinationRabbitmq()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.SUCCEEDED


@mock.patch("destination_rabbitmq.destination.BlockingConnection")
def test_check_fails_on_getting_channel(connection_init):
    connection = Mock()
    connection_init.return_value = connection
    connection.channel.side_effect = Exception("Failed to get channel")
    destination = DestinationRabbitmq()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.FAILED


@mock.patch("destination_rabbitmq.destination.BlockingConnection")
def test_check_fails_on_creating_connection(connection_init):
    connection_init.side_effect = Exception("Could not open connection")
    destination = DestinationRabbitmq()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.FAILED


def _state() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={}))


def _record(stream: str, data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=0))


def _configured_catalog() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"name": {"type": "string"}, "email": {"type": "string"}}}
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="people", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


@mock.patch("destination_rabbitmq.destination.BlockingConnection")
def test_write_succeeds(connection_init):
    stream = "people"
    data = {"name": "John Doe", "email": "john.doe@example.com"}
    channel = _init_mocks(connection_init=connection_init)
    input_messages = [_record(stream=stream, data=data), _state()]
    destination = DestinationRabbitmq()
    for m in destination.write(config=config, configured_catalog=_configured_catalog(), input_messages=input_messages):
        assert m.type == Type.STATE
    _, _, args = channel.basic_publish.mock_calls[0]
    assert args["exchange"] == "test_exchange"
    assert args["routing_key"] == "test_routing_key"
    assert args["properties"].content_type == "application/json"
    assert args["properties"].headers["stream"] == stream
    assert json.loads(args["body"]) == data


@mock.patch("destination_rabbitmq.destination.BlockingConnection")
def test_write_succeeds_with_direct_exchange(connection_init):
    stream = "people"
    data = {"name": "John Doe", "email": "john.doe@example.com"}
    channel = _init_mocks(connection_init=connection_init)
    input_messages = [_record(stream=stream, data=data), _state()]
    custom_config = dict(config)
    del custom_config["exchange"]
    destination = DestinationRabbitmq()
    for m in destination.write(config=custom_config, configured_catalog=_configured_catalog(), input_messages=input_messages):
        assert m.type == Type.STATE
    _, _, args = channel.basic_publish.mock_calls[0]
    assert args["exchange"] == ""
    assert json.loads(args["body"]) == data


@mock.patch("destination_rabbitmq.destination.BlockingConnection")
def test_write_skips_message_from_unknown_stream(connection_init):
    stream = "shapes"
    data = {"name": "Rectangle", "color": "blue"}
    channel = _init_mocks(connection_init=connection_init)
    input_messages = [_record(stream=stream, data=data), _state()]
    destination = DestinationRabbitmq()
    for m in destination.write(config=config, configured_catalog=_configured_catalog(), input_messages=input_messages):
        assert m.type == Type.STATE
    channel.basic_publish.assert_not_called()
