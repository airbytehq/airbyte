#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from typing import Optional

from airbyte_cdk.sources.streams import Stream


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


class LegacyErrorMessageParser(ErrorMessageParser):
    """
    This class acts as an adapter between the new ErrorMessageParser interface and the legacy Stream interface

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream):
        self._stream = stream

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Always delegate to the stream's get_error_display_message method.
        """
        return self._stream.get_error_display_message(exception)
