#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC, abstractmethod


class AbstractDiscoverErrorHandler(ABC):
    """Abstract class for handling exceptions that occur during the discover process."""
    @abstractmethod
    def handle_discover_error(self, logger: logging.Logger, exception: Exception) -> None:
        """
        Handles exceptions that occur during the discover process. This method should an exception if the error is unrecoverable. Override this method to implement custom error handling logic.
        """
        pass


class DefaultDiscoverErrorHandler(AbstractDiscoverErrorHandler):
    """Default implementation of the discover error handler. Raises all exceptions."""
    def handle_discover_error(self, logger: logging.Logger, exception: Exception) -> None:
        raise exception
