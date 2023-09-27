#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.sources.streams.core import StreamData
from deprecated.classic import deprecated

FieldPath = Union[str, List[str]]


@deprecated("This class is experimental. Use at your own risk.")
class AbstractStream(ABC):
    """
    AbstractStream is an experimental interface for streams developed as part of the Concurrent CDK.
    This interface is not yet stable and may change in the future. Use at your own risk.

    Why create a new interface instead of adding concurrency capabilities the existing Stream?
    We learnt a lot since the initial design of the Stream interface, and we wanted to take the opportunity to improve.

    High level, the changes we are targeting are:
    - Removing superfluous or leaky parameters from the methods' interfaces
    - Using composition instead of inheritance to add new capabilities

    To allow us to iterate fast while ensuring backwards compatibility, we are creating a new interface with a facade object that will bridge the old and the new interfaces.
    Source connectors that which to leverage concurrency need to implement this new interface. An example will be available shortly

    Current restrictions on sources that implement this interface. Not all of these restrictions will be lifted in the future, but most will as we iterate on the design.
    - Only full refresh is supported. This will be addressed in the future.
    - The read method does not accept a cursor_field. Streams must be internally aware of the cursor field to use. User-defined cursor fields can be implemented by modifying the connector's main method to instantiate the streams with the configured cursor field.
    - Streams cannot return user-friendly messages by overriding Stream.get_error_display_message. This will be addressed in the future.
    - The Stream's behavior cannot depend on a namespace
    - TypeTransformer is not supported. This will be addressed in the future.
    - Nested cursor and primary keys are not supported
    """

    @abstractmethod
    def read(self) -> Iterable[StreamData]:
        """
        Read a stream in full refresh mode
        :return: The stream's records
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: The stream name
        """

    @property
    def logger(self) -> logging.Logger:
        """
        :return: The logger object
        """
        return logging.getLogger(f"airbyte.streams.{self.name}")

    @property
    @abstractmethod
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
        """
        pass

    @property
    @abstractmethod
    def primary_key(self) -> Optional[FieldPath]:
        """
        :return: A string if single primary key, list of strings if composite primary key.
          Primary keys in nested fields are not supported.
          If the stream has no primary keys, return None.
        """

    @abstractmethod
    def check_availability(self) -> Tuple[bool, Optional[str]]:
        """
        Checks whether this stream is available.

        :return: A tuple of (boolean, str). If boolean is true, then this stream
          is available, and no str is required. Otherwise, this stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """

    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.
        """

    @abstractmethod
    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
