#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import traceback
from datetime import datetime

from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, FailureType, TraceType
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets


class AirbyteTracedException(Exception):
    """
    An exception that should be emitted as an AirbyteTraceMessage
    """

    def __init__(
        self,
        internal_message: str = None,
        message: str = None,
        failure_type: FailureType = FailureType.system_error,
        exception: BaseException = None,
    ):
        """
        :param internal_message: the internal error that caused the failure
        :param message: a user-friendly message that indicates the cause of the error
        :param failure_type: the type of error
        :param exception: the exception that caused the error, from which the stack trace should be retrieved
        """
        self.internal_message = internal_message
        self.message = message
        self.failure_type = failure_type
        self._exception = exception
        super().__init__(internal_message)

    def as_airbyte_message(self) -> AirbyteMessage:
        """
        Builds an AirbyteTraceMessage from the exception
        """
        now_millis = datetime.now().timestamp() * 1000.0

        trace_exc = self._exception or self
        stack_trace_str = "".join(traceback.TracebackException.from_exception(trace_exc).format())

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=now_millis,
            error=AirbyteErrorTraceMessage(
                message=self.message or "Something went wrong in the connector. See the logs for more details.",
                internal_message=self.internal_message,
                failure_type=self.failure_type,
                stack_trace=stack_trace_str,
            ),
        )

        return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)

    def emit_message(self):
        """
        Prints the exception as an AirbyteTraceMessage.
        Note that this will be called automatically on uncaught exceptions when using the airbyte_cdk entrypoint.
        """
        message = self.as_airbyte_message().json(exclude_unset=True)
        filtered_message = filter_secrets(message)
        print(filtered_message)

    @classmethod
    def from_exception(cls, exc: Exception, *args, **kwargs) -> "AirbyteTracedException":
        """
        Helper to create an AirbyteTracedException from an existing exception
        :param exc: the exception that caused the error
        """
        return cls(internal_message=str(exc), exception=exc, *args, **kwargs)
