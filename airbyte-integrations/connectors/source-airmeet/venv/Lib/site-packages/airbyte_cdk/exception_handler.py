#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from types import TracebackType
from typing import Any, List, Mapping, Optional

from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def assemble_uncaught_exception(
    exception_type: type[BaseException], exception_value: BaseException
) -> AirbyteTracedException:
    if issubclass(exception_type, AirbyteTracedException):
        return exception_value  # type: ignore  # validated as part of the previous line
    return AirbyteTracedException.from_exception(exception_value)


def init_uncaught_exception_handler(logger: logging.Logger) -> None:
    """
    Handles uncaught exceptions by emitting an AirbyteTraceMessage and making sure they are not
    printed to the console without having secrets removed.
    """

    def hook_fn(
        exception_type: type[BaseException],
        exception_value: BaseException,
        traceback_: Optional[TracebackType],
    ) -> Any:
        # For developer ergonomics, we want to see the stack trace in the logs when we do a ctrl-c
        if issubclass(exception_type, KeyboardInterrupt):
            sys.__excepthook__(exception_type, exception_value, traceback_)
            return

        logger.fatal(exception_value, exc_info=exception_value)

        # emit an AirbyteTraceMessage for any exception that gets to this spot
        traced_exc = assemble_uncaught_exception(exception_type, exception_value)

        traced_exc.emit_message()

    sys.excepthook = hook_fn


def generate_failed_streams_error_message(stream_failures: Mapping[str, List[Exception]]) -> str:
    failures = "\n".join(
        [
            f"{stream}: {filter_secrets(exception.__repr__())}"
            for stream, exceptions in stream_failures.items()
            for exception in exceptions
        ]
    )
    return f"During the sync, the following streams did not sync successfully: {failures}"
