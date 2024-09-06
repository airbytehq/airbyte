#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Optional

from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, InvalidSchemaError, SchemaInferenceError
from airbyte_cdk.sources.utils.discover_error_handler import AbstractDiscoverErrorHandler


class FileBasedDiscoverErrorHandler(AbstractDiscoverErrorHandler):
    def handle_discover_error(self, logger: logging.Logger, exception: Exception) -> Optional[Exception]:
        """
        Default File Based source implementation of the discover error handler. Logs the error or raises the exception.
        """
        exceptions_to_log = (InvalidSchemaError, SchemaInferenceError, ConfigValidationError)

        if isinstance(exception, exceptions_to_log):
            logger.error(
                f"Error occurred while discovering stream and therefore stream will not be added to the configured catalog: {exception}",
                exc_info=True,
            )
            return None
        else:
            return exception
