#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteTraceMessage,
    FailureType,
    Status,
    StreamDescriptor,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from orjson import orjson

_AN_EXCEPTION = ValueError("An exception")
_A_STREAM_DESCRIPTOR = StreamDescriptor(name="a_stream")
_ANOTHER_STREAM_DESCRIPTOR = StreamDescriptor(name="another_stream")


@pytest.fixture
def raised_exception():
    try:
        raise RuntimeError("an error has occurred")
    except RuntimeError as e:
        return e


def test_build_from_existing_exception(raised_exception):
    traced_exc = AirbyteTracedException.from_exception(raised_exception, message="my user-friendly message")
    assert traced_exc.message == "my user-friendly message"
    assert traced_exc.internal_message == "an error has occurred"
    assert traced_exc.failure_type == FailureType.system_error
    assert traced_exc._exception == raised_exception


def test_exception_as_airbyte_message():
    traced_exc = AirbyteTracedException("an internal message")
    airbyte_message = traced_exc.as_airbyte_message()

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.TRACE
    assert airbyte_message.trace.type == TraceType.ERROR
    assert airbyte_message.trace.emitted_at > 0
    assert airbyte_message.trace.error.failure_type == FailureType.system_error
    assert airbyte_message.trace.error.message == "Something went wrong in the connector. See the logs for more details."
    assert airbyte_message.trace.error.internal_message == "an internal message"
    assert airbyte_message.trace.error.stack_trace == "airbyte_cdk.utils.traced_exception.AirbyteTracedException: an internal message\n"


def test_existing_exception_as_airbyte_message(raised_exception):
    traced_exc = AirbyteTracedException.from_exception(raised_exception)
    airbyte_message = traced_exc.as_airbyte_message()

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.TRACE
    assert airbyte_message.trace.type == TraceType.ERROR
    assert airbyte_message.trace.error.message == "Something went wrong in the connector. See the logs for more details."
    assert airbyte_message.trace.error.internal_message == "an error has occurred"
    assert airbyte_message.trace.error.stack_trace.startswith("Traceback (most recent call last):")
    assert airbyte_message.trace.error.stack_trace.endswith(
        'raise RuntimeError("an error has occurred")\n' "RuntimeError: an error has occurred\n"
    )


def test_config_error_as_connection_status_message():
    traced_exc = AirbyteTracedException("an internal message", message="Config validation error", failure_type=FailureType.config_error)
    airbyte_message = traced_exc.as_connection_status_message()

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.CONNECTION_STATUS
    assert airbyte_message.connectionStatus.status == Status.FAILED
    assert airbyte_message.connectionStatus.message == "Config validation error"


def test_other_error_as_connection_status_message():
    traced_exc = AirbyteTracedException("an internal message", failure_type=FailureType.system_error)
    airbyte_message = traced_exc.as_connection_status_message()

    assert airbyte_message is None


def test_emit_message(capsys):
    traced_exc = AirbyteTracedException(
        internal_message="internal message", message="user-friendly message", exception=RuntimeError("oh no")
    )

    expected_message = AirbyteMessage(
        type=MessageType.TRACE,
        trace=AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=0.0,
            error=AirbyteErrorTraceMessage(
                failure_type=FailureType.system_error,
                message="user-friendly message",
                internal_message="internal message",
                stack_trace="RuntimeError: oh no\n",
            ),
        ),
    )

    traced_exc.emit_message()

    stdout = capsys.readouterr().out
    printed_message = AirbyteMessageSerializer.load(orjson.loads(stdout))
    printed_message.trace.emitted_at = 0.0
    assert printed_message == expected_message


def test_given_both_init_and_as_message_with_stream_descriptor_when_as_airbyte_message_use_init_stream_descriptor() -> None:
    traced_exc = AirbyteTracedException(stream_descriptor=_A_STREAM_DESCRIPTOR)
    message = traced_exc.as_airbyte_message(stream_descriptor=_ANOTHER_STREAM_DESCRIPTOR)
    assert message.trace.error.stream_descriptor == _A_STREAM_DESCRIPTOR


def test_given_both_init_and_as_sanitized_airbyte_message_with_stream_descriptor_when_as_airbyte_message_use_init_stream_descriptor() -> None:
    traced_exc = AirbyteTracedException(stream_descriptor=_A_STREAM_DESCRIPTOR)
    message = traced_exc.as_sanitized_airbyte_message(stream_descriptor=_ANOTHER_STREAM_DESCRIPTOR)
    assert message.trace.error.stream_descriptor == _A_STREAM_DESCRIPTOR


def test_given_both_from_exception_and_as_message_with_stream_descriptor_when_as_airbyte_message_use_init_stream_descriptor() -> None:
    traced_exc = AirbyteTracedException.from_exception(_AN_EXCEPTION, stream_descriptor=_A_STREAM_DESCRIPTOR)
    message = traced_exc.as_airbyte_message(stream_descriptor=_ANOTHER_STREAM_DESCRIPTOR)
    assert message.trace.error.stream_descriptor == _A_STREAM_DESCRIPTOR


def test_given_both_from_exception_and_as_sanitized_airbyte_message_with_stream_descriptor_when_as_airbyte_message_use_init_stream_descriptor() -> None:
    traced_exc = AirbyteTracedException.from_exception(_AN_EXCEPTION, stream_descriptor=_A_STREAM_DESCRIPTOR)
    message = traced_exc.as_sanitized_airbyte_message(stream_descriptor=_ANOTHER_STREAM_DESCRIPTOR)
    assert message.trace.error.stream_descriptor == _A_STREAM_DESCRIPTOR
