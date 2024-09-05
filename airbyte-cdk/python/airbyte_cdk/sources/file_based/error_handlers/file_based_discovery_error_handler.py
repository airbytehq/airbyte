#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from airbyte_cdk.sources.utils.discover_error_handler import AbstractDiscoverErrorHandler
from airbyte_cdk.sources.file_based.exceptions import InvalidSchemaError, SchemaInferenceError


class FileBasedDiscoverErrorHandler(AbstractDiscoverErrorHandler):

    def handle_discover_error(self, logger: logging.Logger, exception: Exception, name: str) -> None:
        """
        Default File Based source implementation of the discover error handler. Logs the error or raises the exception.
        """
        exceptions_to_log = (
            InvalidSchemaError,
            SchemaInferenceError
        )

        if isinstance(exception, exceptions_to_log):
            logger.warn(f"Error occurred while discovering stream {name} and therefore stream will not be added to the configured catalog: {exception}", exc_info=True)
        else:
            raise exception
