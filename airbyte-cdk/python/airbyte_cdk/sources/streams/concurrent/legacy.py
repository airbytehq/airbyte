#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from functools import lru_cache
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.availability_strategy import AbstractAvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from deprecated.classic import deprecated

"""
This module contains adapters to help enabling concurrency on existing Stream without needing to migrate to AbstractStream
"""


@deprecated("This class is experimental. Use at your own risk.")
class StreamFacade(Stream):
    """
    The StreamFacade is a Stream that wraps an AbstractStream and exposes it as a Stream.

    All methods either delegate to the wrapped AbstractStream or provide a default implementation.
    The default implementations define restrictions imposed on Streams migrated to the new interface. For instance, only source-defined cursors are supported.
    """

    def __init__(self, stream: AbstractStream):
        """
        :param stream: The underlying AbstractStream
        """
        self._stream = stream

    def read_full_refresh(
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
    ) -> Iterable[StreamData]:
        """
        Read full refresh. Delegate to the underlying AbstractStream, ignoring all the parameters
        :param cursor_field: (ignored)
        :param logger: (ignored)
        :param slice_logger: (ignored)
        :return: Iterable of StreamData
        """
        for record in self._stream.read():
            yield record.data

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        if sync_mode == SyncMode.full_refresh:
            for record in self._stream.read():
                yield record.data
        else:
            # Incremental reads are not supported
            raise NotImplementedError

    @property
    def name(self) -> str:
        return self._stream.name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._stream.primary_key

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self._stream.cursor_field is None:
            return []
        else:
            return self._stream.cursor_field

    @property
    def source_defined_cursor(self) -> bool:
        # Streams must be aware of their cursor at instantiation time
        return True

    @lru_cache(maxsize=None)
    def get_json_schema(self) -> Mapping[str, Any]:
        return self._stream.get_json_schema()

    @property
    def supports_incremental(self) -> bool:
        # Only full refresh is supported
        return False

    def check_availability(self, logger: logging.Logger, source: Optional["Source"] = None) -> Tuple[bool, Optional[str]]:
        """
        Verifies the stream is available. Delegates to the underlying AbstractStream and ignores the parameters
        :param logger: (ignored)
        :param source:  (ignored)
        :return:
        """
        return self._stream.check_availability()

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        """
        Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.

        The default implementation of this method does not return user-friendly messages for any exception type, but it should be overriden as needed.

        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error
        """
        return self._stream.get_error_display_message(exception)


@deprecated("This class is experimental. Use at your own risk.")
class AvailabilityStrategyFacade(AvailabilityStrategy):
    def __init__(self, abstract_availability_strategy: AbstractAvailabilityStrategy):
        self._abstract_availability_strategy = abstract_availability_strategy

    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        Important to note that the stream and source parameters are not used by the underlying AbstractAvailabilityStrategy.

        :param stream: (unused)
        :param logger: logger object to use
        :param source: (unused)
        :return: A tuple of (boolean, str). If boolean is true, then the stream
        """
        stream_availability = self._abstract_availability_strategy.check_availability(logger)
        return stream_availability.is_available(), stream_availability.message()
