#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils import casing
from airbyte_cdk.sources.utils.transform import TypeTransformer
from airbyte_cdk.sources.utils.types import StreamData
from deprecated.classic import deprecated


@deprecated("This class is experimental. Use at your own risk.")
class AbstractStream(ABC):
    """
    AbstractStream is an experimental interface for Streams developed as part of the Concurrent CDK.
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
    """

    @abstractmethod
    def read(self) -> Iterable[StreamData]:
        """
        Read a stream in full refresh mode
        :return: The stream's records
        """

    @property
    def name(self) -> str:
        """
        :return: Stream name. By default, this is the implementing class name, but it can be overridden as needed.
        """
        return casing.camel_to_snake(self.__class__.__name__)

    @property
    def logger(self) -> logging.Logger:
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
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.
        """

    @property
    @abstractmethod
    def transformer(self) -> TypeTransformer:
        """

        :return:
        """

    def check_availability(self) -> Tuple[bool, Optional[str]]:
        """
        Checks whether this stream is available.

        :return: A tuple of (boolean, str). If boolean is true, then this stream
          is available, and no str is required. Otherwise, this stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """


@deprecated("This class is experimental. Use at your own risk.")
class StreamFacade(Stream):
    """
    The StreamFacade is a Stream that wraps an AbstractStream and exposes it as a Stream.

    All methods either delegate to the wrapped AbstractStream or provide a default implementation.
    The default implementations define restrictions imposed on Streams migrated to the new interface. For instance, only source-defined cursors are supported.
    """

    def __init__(self, stream: AbstractStream):
        self._stream = stream

    @property
    def name(self) -> str:
        return self._stream.name

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        return self._stream.read()

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._stream.primary_key

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return self._stream.cursor_field

    @property
    def source_defined_cursor(self) -> bool:
        # Streams must be aware of their cursor at instantiation time
        return True

    @property
    def transformer(self) -> TypeTransformer:
        return self._stream.transformer

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._stream.get_json_schema()

    @property
    def supports_incremental(self) -> bool:
        # Only full refresh is supported
        return False
