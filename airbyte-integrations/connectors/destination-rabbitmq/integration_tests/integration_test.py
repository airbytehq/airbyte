#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

from destination_rabbitmq.destination import DestinationRabbitmq, create_connection

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


TEST_STREAM = "animals"
TEST_NAMESPACE = "test_namespace"
TEST_MESSAGE = {"name": "cat"}


def _configured_catalog() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=TEST_STREAM, json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


def consume(config):
    connection = create_connection(config=config)
    channel = connection.channel()

    def assert_message(ch, method, properties, body):
        assert json.loads(body) == TEST_MESSAGE
        assert properties.content_type == "application/json"
        assert properties.headers["stream"] == TEST_STREAM
        assert properties.headers["namespace"] == TEST_NAMESPACE
        assert "emitted_at" in properties.headers
        channel.stop_consuming()

    channel.basic_consume(queue=config["routing_key"], on_message_callback=assert_message, auto_ack=True)
    channel.start_consuming()


def _state() -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={}))


def _record() -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=TEST_STREAM, data=TEST_MESSAGE, emitted_at=0, namespace=TEST_NAMESPACE)
    )


def test_check_fails():
    f = open(
        "integration_tests/invalid_config.json",
    )
    config = json.load(f)
    destination = DestinationRabbitmq()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.FAILED


def test_check_succeeds():
    f = open(
        "secrets/config.json",
    )
    config = json.load(f)
    destination = DestinationRabbitmq()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.SUCCEEDED


def test_write():
    f = open(
        "secrets/config.json",
    )
    config = json.load(f)
    messages = [_record(), _state()]
    destination = DestinationRabbitmq()
    for m in destination.write(config=config, configured_catalog=_configured_catalog(), input_messages=messages):
        assert m.type == Type.STATE
    consume(config)
