#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import sys

from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def init_uncaught_exception_handler(logger: logging.Logger) -> None:
    """
    Handles uncaught exceptions by emitting an AirbyteTraceMessage and making sure they are not
    printed to the console without having secrets removed.
    """

    def hook_fn(exception_type, exception_value, traceback_):
        # For developer ergonomics, we want to see the stack trace in the logs when we do a ctrl-c
        if issubclass(exception_type, KeyboardInterrupt):
            sys.__excepthook__(exception_type, exception_value, traceback_)
            return

        logger.fatal(exception_value, exc_info=exception_value)

        # emit an AirbyteTraceMessage for any exception that gets to this spot
        traced_exc = (
            exception_value
            if issubclass(exception_type, AirbyteTracedException)
            else AirbyteTracedException.from_exception(exception_value)
        )

        traced_exc.emit_message()

    sys.excepthook = hook_fn
