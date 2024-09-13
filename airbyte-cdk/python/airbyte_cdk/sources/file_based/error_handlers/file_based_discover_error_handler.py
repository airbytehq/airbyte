#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import List, Union

from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_cdk.sources.file_based.exceptions import FileBasedSourceError
from airbyte_cdk.sources.utils.discover_error_handler import AbstractDiscoverErrorHandler


class FileBasedDiscoverErrorHandler(AbstractDiscoverErrorHandler):
    """Default File Based source implementation of the discover error handler. Logs the error or raises the exception."""

    def __init__(self, exceptions_to_log: List[type[Exception]], underlying_exceptions_to_log: List[Union[FileBasedSourceError, str]]) -> None:
        self._exceptions_to_log = exceptions_to_log or []
        self._underlying_exceptions_to_log = [
            exc.value if isinstance(exc, FileBasedSourceError) else exc
            for exc in underlying_exceptions_to_log
        ] or []

    def handle_discover_error(self, logger: logging.Logger, exception: Exception) -> None:
        if type(exception) in self._exceptions_to_log:
            logger.error(f"Error occurred while discovering stream and therefore stream will not be added to the configured catalog: {exception}")
        elif isinstance(exception, AirbyteTracedException) and exception.message is not None and any(exc in exception.message for exc in self._underlying_exceptions_to_log):
            logger.error(f"Error occurred while discovering stream and therefore stream will not be added to the configured catalog: {exception}")
        else:
            raise exception
