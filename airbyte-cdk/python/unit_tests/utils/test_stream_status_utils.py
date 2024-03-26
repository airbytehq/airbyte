#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteMessage, AirbyteStream, AirbyteStreamStatus, SyncMode, TraceType
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message as stream_status_as_airbyte_message

stream = AirbyteStream(name="name", namespace="namespace", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])


def test_started_as_message():
    stream_status = AirbyteStreamStatus.STARTED
    airbyte_message = stream_status_as_airbyte_message(stream, stream_status)

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.TRACE
    assert airbyte_message.trace.type == TraceType.STREAM_STATUS
    assert airbyte_message.trace.emitted_at > 0
    assert airbyte_message.trace.stream_status.stream_descriptor.name == stream.name
    assert airbyte_message.trace.stream_status.stream_descriptor.namespace == stream.namespace
    assert airbyte_message.trace.stream_status.status == stream_status


def test_running_as_message():
    stream_status = AirbyteStreamStatus.RUNNING
    airbyte_message = stream_status_as_airbyte_message(stream, stream_status)

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.TRACE
    assert airbyte_message.trace.type == TraceType.STREAM_STATUS
    assert airbyte_message.trace.emitted_at > 0
    assert airbyte_message.trace.stream_status.stream_descriptor.name == stream.name
    assert airbyte_message.trace.stream_status.stream_descriptor.namespace == stream.namespace
    assert airbyte_message.trace.stream_status.status == stream_status


def test_complete_as_message():
    stream_status = AirbyteStreamStatus.COMPLETE
    airbyte_message = stream_status_as_airbyte_message(stream, stream_status)

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.TRACE
    assert airbyte_message.trace.type == TraceType.STREAM_STATUS
    assert airbyte_message.trace.emitted_at > 0
    assert airbyte_message.trace.stream_status.stream_descriptor.name == stream.name
    assert airbyte_message.trace.stream_status.stream_descriptor.namespace == stream.namespace
    assert airbyte_message.trace.stream_status.status == stream_status


def test_incomplete_failed_as_message():
    stream_status = AirbyteStreamStatus.INCOMPLETE
    airbyte_message = stream_status_as_airbyte_message(stream, stream_status)

    assert isinstance(airbyte_message, AirbyteMessage)
    assert airbyte_message.type == MessageType.TRACE
    assert airbyte_message.trace.type == TraceType.STREAM_STATUS
    assert airbyte_message.trace.emitted_at > 0
    assert airbyte_message.trace.stream_status.stream_descriptor.name == stream.name
    assert airbyte_message.trace.stream_status.stream_descriptor.namespace == stream.namespace
    assert airbyte_message.trace.stream_status.status == stream_status
