#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.core import Stream, StreamData

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


# FIXME this
class AvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability.
    """

    @abstractmethod
    def check_availability(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """

    @staticmethod
    def get_first_stream_slice(stream: Stream) -> Optional[Mapping[str, Any]]:
        """
        Gets the first stream_slice from a given stream's stream_slices.
        :param stream: stream
        :raises StopIteration: if there is no first slice to return (the stream_slices generator is empty)
        :return: first stream slice from 'stream_slices' generator (`None` is a valid stream slice)
        """
        # We wrap the return output of stream_slices() because some implementations return types that are iterable,
        # but not iterators such as lists or tuples
        slices = iter(
            stream.stream_slices(
                cursor_field=stream.cursor_field,  # type: ignore[arg-type]
                sync_mode=SyncMode.full_refresh,
            )
        )
        return next(slices)

    @staticmethod
    def get_first_record_for_slice(
        stream: Stream, stream_slice: Optional[Mapping[str, Any]]
    ) -> StreamData:
        """
        Gets the first record for a stream_slice of a stream.

        :param stream: stream instance from which to read records
        :param stream_slice: stream_slice parameters for slicing the stream
        :raises StopIteration: if there is no first record to return (the read_records generator is empty)
        :return: StreamData containing the first record in the slice
        """
        # Store the original value of exit_on_rate_limit
        original_exit_on_rate_limit = stream.exit_on_rate_limit

        try:
            # Ensure exit_on_rate_limit is safely set to True if possible
            stream.exit_on_rate_limit = True

            # We wrap the return output of read_records() because some implementations return types that are iterable,
            # but not iterators such as lists or tuples
            records_for_slice = iter(
                stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            )

            return next(records_for_slice)
        finally:
            # Restore the original exit_on_rate_limit value
            stream.exit_on_rate_limit = original_exit_on_rate_limit
