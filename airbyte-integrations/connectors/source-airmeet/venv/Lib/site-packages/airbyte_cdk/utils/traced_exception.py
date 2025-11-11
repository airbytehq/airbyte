#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import time
import traceback
from typing import Any, Optional

import orjson

from airbyte_cdk.models import (
    AirbyteConnectionStatus,
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
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets


class AirbyteTracedException(Exception):
    """
    An exception that should be emitted as an AirbyteTraceMessage
    """

    def __init__(
        self,
        internal_message: Optional[str] = None,
        message: Optional[str] = None,
        failure_type: FailureType = FailureType.system_error,
        exception: Optional[BaseException] = None,
        stream_descriptor: Optional[StreamDescriptor] = None,
    ):
        """
        :param internal_message: the internal error that caused the failure
        :param message: a user-friendly message that indicates the cause of the error
        :param failure_type: the type of error
        :param exception: the exception that caused the error, from which the stack trace should be retrieved
        :param stream_descriptor: describe the stream from which the exception comes from
        """
        self.internal_message = internal_message
        self.message = message
        self.failure_type = failure_type
        self._exception = exception
        self._stream_descriptor = stream_descriptor
        super().__init__(internal_message)

    def as_airbyte_message(
        self, stream_descriptor: Optional[StreamDescriptor] = None
    ) -> AirbyteMessage:
        """
        Builds an AirbyteTraceMessage from the exception

        :param stream_descriptor is deprecated, please use the stream_description in `__init__ or `from_exception`. If many
          stream_descriptors are defined, the one from `as_airbyte_message` will be discarded.
        """
        now_millis = time.time_ns() // 1_000_000

        trace_exc = self._exception or self
        stack_trace_str = "".join(traceback.TracebackException.from_exception(trace_exc).format())

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=now_millis,
            error=AirbyteErrorTraceMessage(
                message=self.message
                or "Something went wrong in the connector. See the logs for more details.",
                internal_message=self.internal_message,
                failure_type=self.failure_type,
                stack_trace=stack_trace_str,
                stream_descriptor=self._stream_descriptor
                if self._stream_descriptor is not None
                else stream_descriptor,
            ),
        )

        return AirbyteMessage(type=MessageType.TRACE, trace=trace_message)

    def as_connection_status_message(self) -> Optional[AirbyteMessage]:
        if self.failure_type == FailureType.config_error:
            return AirbyteMessage(
                type=MessageType.CONNECTION_STATUS,
                connectionStatus=AirbyteConnectionStatus(
                    status=Status.FAILED, message=self.message
                ),
            )
        return None

    def emit_message(self) -> None:
        """
        Prints the exception as an AirbyteTraceMessage.
        Note that this will be called automatically on uncaught exceptions when using the airbyte_cdk entrypoint.
        """
        message = orjson.dumps(AirbyteMessageSerializer.dump(self.as_airbyte_message())).decode()
        filtered_message = filter_secrets(message)
        print(filtered_message)

    @classmethod
    def from_exception(
        cls,
        exc: BaseException,
        stream_descriptor: Optional[StreamDescriptor] = None,
        *args: Any,
        **kwargs: Any,
    ) -> "AirbyteTracedException":
        """
        Helper to create an AirbyteTracedException from an existing exception
        :param exc: the exception that caused the error
        :param stream_descriptor: describe the stream from which the exception comes from
        """
        return cls(
            internal_message=str(exc),
            exception=exc,
            stream_descriptor=stream_descriptor,
            *args,
            **kwargs,
        )  # type: ignore  # ignoring because of args and kwargs

    def as_sanitized_airbyte_message(
        self, stream_descriptor: Optional[StreamDescriptor] = None
    ) -> AirbyteMessage:
        """
        Builds an AirbyteTraceMessage from the exception and sanitizes any secrets from the message body

        :param stream_descriptor is deprecated, please use the stream_description in `__init__ or `from_exception`. If many
          stream_descriptors are defined, the one from `as_sanitized_airbyte_message` will be discarded.
        """
        error_message = self.as_airbyte_message(stream_descriptor=stream_descriptor)
        if error_message.trace.error.message:  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
            error_message.trace.error.message = filter_secrets(  # type: ignore[union-attr]
                error_message.trace.error.message,  # type: ignore[union-attr]
            )
        if error_message.trace.error.internal_message:  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
            error_message.trace.error.internal_message = filter_secrets(  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
                error_message.trace.error.internal_message  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
            )
        if error_message.trace.error.stack_trace:  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
            error_message.trace.error.stack_trace = filter_secrets(  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
                error_message.trace.error.stack_trace  # type: ignore[union-attr] # AirbyteMessage with MessageType.TRACE has AirbyteTraceMessage
            )
        return error_message
