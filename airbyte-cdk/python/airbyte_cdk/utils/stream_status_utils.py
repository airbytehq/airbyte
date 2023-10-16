#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteStream,
    StreamDescriptor,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType


def as_airbyte_message(stream: ConfiguredAirbyteStream, current_status: AirbyteStreamStatus) -> AirbyteMessage:
    """
    Builds an AirbyteStreamStatusTraceMessage for the provided stream
    """

    now_millis = datetime.now().timestamp() * 1000.0

    trace_message = AirbyteTraceMessage(
        type=TraceType.STREAM_STATUS,
        emitted_at=now_millis,
        stream_status=AirbyteStreamStatusTraceMessage(
            stream_descriptor=StreamDescriptor(name=stream.stream.name, namespace=stream.stream.namespace),
            status=current_status,
        ),
    )

    return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)
