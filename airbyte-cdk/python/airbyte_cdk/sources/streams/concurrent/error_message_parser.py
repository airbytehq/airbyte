#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Optional


class ErrorMessageParser(ABC):
    """
    This class is used to parse the error message from the exception thrown by the stream.
    """

    @abstractmethod
    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
