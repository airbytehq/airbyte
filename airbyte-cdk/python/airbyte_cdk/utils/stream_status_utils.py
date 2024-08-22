#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from typing import List, Optional, Union

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusReason,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    StreamDescriptor,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType


def as_airbyte_message(
    stream: Union[AirbyteStream, StreamDescriptor],
    current_status: AirbyteStreamStatus,
    reasons: Optional[List[AirbyteStreamStatusReason]] = None,
) -> AirbyteMessage:
    """
    Builds an AirbyteStreamStatusTraceMessage for the provided stream
    """

    now_millis = datetime.now().timestamp() * 1000.0

    trace_message = AirbyteTraceMessage(
        type=TraceType.STREAM_STATUS,
        emitted_at=now_millis,
        stream_status=AirbyteStreamStatusTraceMessage(
            stream_descriptor=StreamDescriptor(name=stream.name, namespace=stream.namespace),
            status=current_status,
            reasons=reasons,
        ),
    )

    return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)
