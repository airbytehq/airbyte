#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteTraceMessage,
    Level,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils.record_helper import stream_data_to_airbyte_message

NOW = 1234567
STREAM_NAME = "my_stream"


@pytest.mark.parametrize(
    "test_name, data, expected_message",
    [
        (
            "test_data_to_airbyte_record",
            {"id": 0, "field_A": 1.0, "field_B": "airbyte"},
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="my_stream", data={"id": 0, "field_A": 1.0, "field_B": "airbyte"}, emitted_at=NOW),
            ),
        ),
        (
            "test_record_to_airbyte_record",
            AirbyteRecordMessage(stream="my_stream", data={"id": 0, "field_A": 1.0, "field_B": "airbyte"}, emitted_at=NOW),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="my_stream", data={"id": 0, "field_A": 1.0, "field_B": "airbyte"}, emitted_at=NOW),
            ),
        ),
    ],
)
def test_data_or_record_to_airbyte_record(test_name, data, expected_message):
    transformer = MagicMock()
    schema = {}
    message = stream_data_to_airbyte_message(STREAM_NAME, data, transformer, schema)
    message.record.emitted_at = NOW

    if isinstance(data, dict):
        transformer.transform.assert_called_with(data, schema)
    else:
        assert not transformer.transform.called
    assert expected_message == message


@pytest.mark.parametrize(
    "test_name, data, expected_message",
    [
        (
            "test_log_message_to_airbyte_record",
            AirbyteLogMessage(level=Level.INFO, message="Hello, this is a log message"),
            AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Hello, this is a log message")),
        ),
        (
            "test_trace_message_to_airbyte_record",
            AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=101),
            AirbyteMessage(type=MessageType.TRACE, trace=AirbyteTraceMessage(type=TraceType.ERROR, emitted_at=101)),
        ),
    ],
)
def test_log_or_trace_to_message(test_name, data, expected_message):
    transformer = MagicMock()
    schema = {}
    message = stream_data_to_airbyte_message(STREAM_NAME, data, transformer, schema)

    assert not transformer.transform.called
    assert expected_message == message


@pytest.mark.parametrize(
    "test_name, data",
    [
        ("test_log_message_to_airbyte_record", AirbyteStateMessage(type=AirbyteStateType.STREAM)),
    ],
)
def test_state_message_to_message(test_name, data):
    transformer = MagicMock()
    schema = {}
    with pytest.raises(ValueError):
        stream_data_to_airbyte_message(STREAM_NAME, data, transformer, schema)
