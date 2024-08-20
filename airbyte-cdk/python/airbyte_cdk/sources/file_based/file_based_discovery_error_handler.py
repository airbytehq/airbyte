#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Optional
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.utils.discover_error_handler import AbstractDiscoverErrorHandler
from airbyte_cdk.sources.file_based.exceptions import SchemaInferenceError, InvalidSchemaError


class FileBasedDiscoverErrorHandler(AbstractDiscoverErrorHandler):

    def __init__(self, errors_to_ignore: Optional[list[Exception]] = None) -> None:
        self._errors_to_ignore = errors_to_ignore or [SchemaInferenceError, InvalidSchemaError]

    def handle_discover_error(self, logger: logging.Logger, exception: Exception, stream: Stream) -> None:
        """
        Default File Based source implementation of the discover error handler. Logs the error or raises the exception.
        """
        if isinstance(exception, AirbyteTracedException):
            exception_type = type(exception._exception)
        else:
            exception_type = type(exception)

        print("\n\n=-=-=-=-=-=-=\n\n")
        print(exception._exception, exception_type, self._errors_to_ignore, exception_type in self._errors_to_ignore)
        print("\n\n=-=-=-=-=-=-=\n\n")
        if exception_type in self._errors_to_ignore:
            print("\n\n=====================\n\n")
            print("Error occurred while discovering stream {stream.name}: {exception}")
            print("\n\n=====================\n\n")
            logger.error(f"Error occurred while discovering stream {stream.name}: {exception}", exc_info=True)
        else:
            raise exception
        return
