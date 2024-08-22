#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    StreamDescriptor,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType


@pytest.fixture
def remove_stack_trace():
    def _remove_stack_trace(message: AirbyteMessage) -> AirbyteMessage:
        """
        Helper method that removes the stack trace from Airbyte trace messages to make asserting against expected records easier
        """
        if message.trace and message.trace.error and message.trace.error.stack_trace:
            message.trace.error.stack_trace = None
        return message

    return _remove_stack_trace


@pytest.fixture
def as_stream_status():
    def _as_stream_status(stream: str, status: AirbyteStreamStatus) -> AirbyteMessage:
        trace_message = AirbyteTraceMessage(
            emitted_at=datetime.datetime.now().timestamp() * 1000.0,
            type=TraceType.STREAM_STATUS,
            stream_status=AirbyteStreamStatusTraceMessage(
                stream_descriptor=StreamDescriptor(name=stream),
                status=status,
            ),
        )

        return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)

    return _as_stream_status
