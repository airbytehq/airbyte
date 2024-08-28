#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.utils.discover_error_handler import AbstractDiscoverErrorHandler
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError


class FileBasedDiscoverErrorHandler(AbstractDiscoverErrorHandler):

    def handle_discover_error(self, logger: logging.Logger, exception: Exception, stream: Stream) -> None:
        """
        Default File Based source implementation of the discover error handler. Logs the error or raises the exception.
        """
        exception_message = exception.message if isinstance(exception, AirbyteTracedException) else str(exception)
        exceptions_to_log = [
            FileBasedSourceError.SCHEMA_INFERENCE_ERROR,
            FileBasedSourceError.INVALID_SCHEMA_ERROR,
        ]

        if any(error.value in exception_message for error in exceptions_to_log):
            logger.error(f"Error occurred while discovering stream {stream.name}: {exception}", exc_info=True)
        else:
            raise exception
