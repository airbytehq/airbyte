#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteStateMessage,
    OrchestratorType,
    Type,
)
from airbyte_cdk.sources.message import InMemoryMessageRepository

A_CONTROL = AirbyteControlMessage(
    type=OrchestratorType.CONNECTOR_CONFIG,
    emitted_at=0,
    connectorConfig=AirbyteControlConnectorConfigMessage(config={"a config": "value"}),
)
ANOTHER_CONTROL = AirbyteControlMessage(
    type=OrchestratorType.CONNECTOR_CONFIG,
    emitted_at=0,
    connectorConfig=AirbyteControlConnectorConfigMessage(config={"another config": "another value"}),
)


def test_given_no_messages_when_consume_queue_then_return_empty():
    repo = InMemoryMessageRepository()
    messages = list(repo.consume_queue())
    assert messages == []


def test_given_messages_when_consume_queue_then_return_messages():
    repo = InMemoryMessageRepository()
    first_message = AirbyteMessage(type=Type.CONTROL, control=A_CONTROL)
    repo.emit_message(first_message)
    second_message = AirbyteMessage(type=Type.CONTROL, control=ANOTHER_CONTROL)
    repo.emit_message(second_message)

    messages = repo.consume_queue()

    assert list(messages) == [first_message, second_message]


def test_given_message_is_consumed_when_consume_queue_then_remove_message_from_queue():
    repo = InMemoryMessageRepository()
    first_message = AirbyteMessage(type=Type.CONTROL, control=A_CONTROL)
    repo.emit_message(first_message)
    second_message = AirbyteMessage(type=Type.CONTROL, control=ANOTHER_CONTROL)
    repo.emit_message(second_message)

    message_generator = repo.consume_queue()
    consumed_message = next(message_generator)
    assert consumed_message == first_message

    second_message_generator = repo.consume_queue()
    assert list(second_message_generator) == [second_message]


def test_given_message_is_not_control_nor_log_message_when_emit_message_then_raise_error():
    repo = InMemoryMessageRepository()
    with pytest.raises(ValueError):
        repo.emit_message(AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"state": "state value"})))
