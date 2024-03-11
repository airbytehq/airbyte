# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_cdk.utils.message_utils import get_stream_descriptor
from airbyte_protocol.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateStats,
    AirbyteStateType,
    AirbyteStreamState,
    OrchestratorType,
    StreamDescriptor,
    Type,
)


def test_get_record_message_stream_descriptor():
    message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="test_stream",
            namespace="test_namespace",
            data={"id": "12345"},
            emitted_at=1,
        ),
    )
    expected_descriptor = HashableStreamDescriptor(name="test_stream", namespace="test_namespace")
    assert get_stream_descriptor(message) == expected_descriptor


def test_get_record_message_stream_descriptor_no_namespace():
    message = AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream="test_stream", data={"id": "12345"}, emitted_at=1
        ),
    )
    expected_descriptor = HashableStreamDescriptor(name="test_stream", namespace=None)
    assert get_stream_descriptor(message) == expected_descriptor


def test_get_state_message_stream_descriptor():
    message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(
                    name="test_stream", namespace="test_namespace"
                ),
                stream_state=AirbyteStateBlob(updated_at="2024-02-02"),
            ),
            sourceStats=AirbyteStateStats(recordCount=27.0),
        ),
    )
    expected_descriptor = HashableStreamDescriptor(name="test_stream", namespace="test_namespace")
    assert get_stream_descriptor(message) == expected_descriptor


def test_get_state_message_stream_descriptor_no_namespace():
    message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="test_stream"),
                stream_state=AirbyteStateBlob(updated_at="2024-02-02"),
            ),
            sourceStats=AirbyteStateStats(recordCount=27.0),
        ),
    )
    expected_descriptor = HashableStreamDescriptor(name="test_stream", namespace=None)
    assert get_stream_descriptor(message) == expected_descriptor


def test_get_other_message_stream_descriptor_fails():
    message = AirbyteMessage(
        type=Type.CONTROL,
        control=AirbyteControlMessage(
            type=OrchestratorType.CONNECTOR_CONFIG,
            emitted_at=10,
            connectorConfig=AirbyteControlConnectorConfigMessage(config={"any config": "a config value"}),
        ),
    )
    with pytest.raises(NotImplementedError):
        get_stream_descriptor(message)
