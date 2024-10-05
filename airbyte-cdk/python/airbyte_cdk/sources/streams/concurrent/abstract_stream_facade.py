# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from airbyte_cdk.sources.streams.concurrent.exceptions import ExceptionWithDisplayMessage

StreamType = TypeVar("StreamType")


class AbstractStreamFacade(Generic[StreamType], ABC):
    @abstractmethod
    def get_underlying_stream(self) -> StreamType:
        """
        Return the underlying stream facade object.
        """
        ...

    @property
    def source_defined_cursor(self) -> bool:
        # Streams must be aware of their cursor at instantiation time
        return True

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        A display message will be returned if the exception is an instance of ExceptionWithDisplayMessage.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        if isinstance(exception, ExceptionWithDisplayMessage):
            return exception.display_message
        else:
            return None
