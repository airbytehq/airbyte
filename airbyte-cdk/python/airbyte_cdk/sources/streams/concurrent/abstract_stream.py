#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, Optional

from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import StreamAvailability
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from deprecated.classic import deprecated


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
    Source connectors that wish to leverage concurrency need to implement this new interface. An example will be available shortly

    Current restrictions on sources that implement this interface. Not all of these restrictions will be lifted in the future, but most will as we iterate on the design.
    - Only full refresh is supported. This will be addressed in the future.
    - The read method does not accept a cursor_field. Streams must be internally aware of the cursor field to use. User-defined cursor fields can be implemented by modifying the connector's main method to instantiate the streams with the configured cursor field.
    - Streams cannot return user-friendly messages by overriding Stream.get_error_display_message. This will be addressed in the future.
    - The Stream's behavior cannot depend on a namespace
    - TypeTransformer is not supported. This will be addressed in the future.
    - Nested cursor and primary keys are not supported
    """

    @abstractmethod
    def generate_partitions(self) -> Iterable[Partition]:
        """
        Generates the partitions that will be read by this stream.
        :return: An iterable of partitions.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: The stream name
        """

    @property
    @abstractmethod
    def cursor_field(self) -> Optional[str]:
        """
        Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. Nested cursor fields are not supported.
        """

    @abstractmethod
    def check_availability(self) -> StreamAvailability:
        """
        :return: The stream's availability
        """

    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.
        """

    @abstractmethod
    def as_airbyte_stream(self) -> AirbyteStream:
        """
        :return: A dict of the JSON schema representing this stream.
        """

    @abstractmethod
    def log_stream_sync_configuration(self) -> None:
        """
        Logs the stream's configuration for debugging purposes.
        """

    @property
    @abstractmethod
    def cursor(self) -> Cursor:
        """
        :return: The cursor associated with this stream.
        """
