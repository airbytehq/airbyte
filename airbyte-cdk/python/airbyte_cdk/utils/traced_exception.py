#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import traceback
from datetime import datetime

from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, FailureType, TraceType
from airbyte_cdk.models import Type as MessageType


class AirbyteTracedException(Exception):
    """
    TODO: give this a meaningful description
    """

    def __init__(
        self,
        internal_message: str = None,
        message: str = None,
        failure_type: FailureType = FailureType.system_error,
        exception: BaseException = None,
    ):
        self.internal_message = internal_message
        self.message = message
        self.failure_type = failure_type
        self._exception = exception
        super().__init__(internal_message)

    def as_airbyte_message(self) -> AirbyteMessage:
        now_millis = int(datetime.now().timestamp() * 1000)

        trace_exc = self._exception or self
        stack_trace_str = "".join(traceback.TracebackException.from_exception(trace_exc).format())

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=now_millis,
            error=AirbyteErrorTraceMessage(
                message=self.message or "an error occurred with the source",
                internal_message=self.internal_message,
                failure_type=self.failure_type,
                stack_trace=stack_trace_str,
            ),
        )

        return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)

    @classmethod
    def from_exception(cls, exc: Exception, *args, **kwargs) -> "AirbyteTracedException":
        return cls(internal_message=str(exc), exception=exc, *args, **kwargs)
