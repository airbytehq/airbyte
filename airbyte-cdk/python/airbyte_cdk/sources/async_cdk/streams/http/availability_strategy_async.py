#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import TYPE_CHECKING, Optional, Tuple

from airbyte_cdk.sources.async_cdk.abstract_source_async import AsyncAbstractSource
from airbyte_cdk.sources.async_cdk.streams.utils.stream_helper_async import (
    get_first_record_for_slice,
    get_first_stream_slice,
)
from airbyte_cdk.sources.streams.http.availability_strategy import (
    HttpAvailabilityStrategy,
)
from airbyte_cdk.sources.streams.http.utils import HttpError

if TYPE_CHECKING:
    from airbyte_cdk.sources.async_cdk.streams.http.http_async import AsyncHttpStream


class AsyncHttpAvailabilityStrategy(HttpAvailabilityStrategy):
    async def check_availability(
        self,
        stream: "AsyncHttpStream",
        logger: logging.Logger,
        source: Optional["AsyncAbstractSource"],
    ) -> Tuple[bool, Optional[str]]:
        """
        Check stream availability by attempting to read the first record of the
        stream.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """
        try:
            # Some streams need a stream slice to read records (e.g. if they have a SubstreamPartitionRouter)
            # Streams that don't need a stream slice will return `None` as their first stream slice.
            stream_slice = await get_first_stream_slice(stream)
        except StopAsyncIteration:
            # If stream_slices has no `next()` item (Note - this is different from stream_slices returning [None]!)
            # This can happen when a substream's `stream_slices` method does a `for record in parent_records: yield <something>`
            # without accounting for the case in which the parent stream is empty.
            reason = f"Cannot attempt to connect to stream {stream.name} - no stream slices were found, likely because the parent stream is empty."
            return False, reason
        except HttpError as error:
            is_available, reason = self._handle_http_error(stream, logger, source, error)
            if not is_available:
                reason = f"Unable to get slices for {stream.name} stream, because of error in parent stream. {reason}"
            return is_available, reason

        try:
            await get_first_record_for_slice(stream, stream_slice)
            return True, None
        except StopAsyncIteration:
            logger.info(
                f"Successfully connected to stream {stream.name}, but got 0 records."
            )
            return True, None
        except HttpError as error:
            is_available, reason = self._handle_http_error(
                stream, logger, source, error
            )
            if not is_available:
                reason = f"Unable to read {stream.name} stream. {reason}"
            return is_available, reason

        return True, None
