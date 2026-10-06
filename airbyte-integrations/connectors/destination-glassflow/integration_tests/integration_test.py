#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

from destination_glassflow.destination import DestinationGlassflow, create_sink_connection

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


TEST_STREAM = "test"
TEST_NAMESPACE = "test_namespace"
TEST_MESSAGE = {"name": "John Smith"}


def _configured_catalog() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {}}
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name=TEST_STREAM, json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


def consume(config):
    connection = create_sink_connection(config=config)

    while True:
        # Consume transformed event from the pipeline
        res = connection.consume()

        if res.status_code == 200:
            record = res.event()
            assert record["data"] == TEST_MESSAGE
            assert record["stream"] == TEST_STREAM
            assert record["namespace"] == TEST_NAMESPACE
            assert "emitted_at" in record
            break


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
    destination = DestinationGlassflow()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.FAILED


def test_check_succeeds():
    f = open(
        "secrets/config.json",
    )
    config = json.load(f)
    destination = DestinationGlassflow()
    status = destination.check(logger=Mock(), config=config)
    assert status.status == Status.SUCCEEDED


def test_write():
    f = open(
        "secrets/config.json",
    )
    config = json.load(f)
    messages = [_record(), _state()]
    destination = DestinationGlassflow()
    for m in destination.write(config=config, configured_catalog=_configured_catalog(), input_messages=messages):
        assert m.type == Type.STATE
    consume(config)
