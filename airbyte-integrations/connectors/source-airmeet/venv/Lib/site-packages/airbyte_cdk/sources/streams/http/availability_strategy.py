#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from typing import Optional, Tuple

from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class HttpAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"] = None
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
        reason: Optional[str]
        try:
            # Some streams need a stream slice to read records (e.g. if they have a SubstreamPartitionRouter)
            # Streams that don't need a stream slice will return `None` as their first stream slice.
            stream_slice = self.get_first_stream_slice(stream)
        except StopIteration:
            # If stream_slices has no `next()` item (Note - this is different from stream_slices returning [None]!)
            # This can happen when a substream's `stream_slices` method does a `for record in parent_records: yield <something>`
            # without accounting for the case in which the parent stream is empty.
            reason = f"Cannot attempt to connect to stream {stream.name} - no stream slices were found, likely because the parent stream is empty."
            return False, reason
        except AirbyteTracedException as error:
            return False, error.message

        try:
            self.get_first_record_for_slice(stream, stream_slice)
            return True, None
        except StopIteration:
            logger.info(f"Successfully connected to stream {stream.name}, but got 0 records.")
            return True, None
        except AirbyteTracedException as error:
            return False, error.message
