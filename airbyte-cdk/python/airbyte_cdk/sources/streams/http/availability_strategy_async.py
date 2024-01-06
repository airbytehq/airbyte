#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from typing import Dict, Optional, Tuple

import requests
from aiohttp import ClientResponseError
from airbyte_cdk.sources.streams import AsyncStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.utils.stream_helper_async import get_first_record_for_slice, get_first_stream_slice

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class AsyncHttpAvailabilityStrategy(HttpAvailabilityStrategy):
    async def check_availability(self, stream: AsyncStream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
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
        except StopIteration:
            # If stream_slices has no `next()` item (Note - this is different from stream_slices returning [None]!)
            # This can happen when a substream's `stream_slices` method does a `for record in parent_records: yield <something>`
            # without accounting for the case in which the parent stream is empty.
            reason = f"Cannot attempt to connect to stream {stream.name} - no stream slices were found, likely because the parent stream is empty."
            return False, reason
        except ClientResponseError as error:
            is_available, reason = await self._handle_http_error(stream, logger, source, error)
            if not is_available:
                reason = f"Unable to get slices for {stream.name} stream, because of error in parent stream. {reason}"
            return is_available, reason

        try:
            async for _ in get_first_record_for_slice(stream, stream_slice):
                return True, None
        except StopIteration:
            logger.info(f"Successfully connected to stream {stream.name}, but got 0 records.")
            return True, None
        except ClientResponseError as error:
            is_available, reason = await self._handle_http_error(stream, logger, source, error)
            if not is_available:
                reason = f"Unable to read {stream.name} stream. {reason}"
            return is_available, reason

    async def _handle_http_error(
        self, stream: AsyncStream, logger: logging.Logger, source: Optional["Source"], error: ClientResponseError
    ) -> Tuple[bool, Optional[str]]:
        """
        Override this method to define error handling for various `HTTPError`s
        that are raised while attempting to check a stream's availability.

        Checks whether an error's status_code is in a list of unavailable_error_codes,
        and gets the associated reason for that error.

        :param stream: stream
        :param logger: source logger
        :param source: optional (source)
        :param error: HTTPError raised while checking stream's availability.
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """
        status_code = error.status
        known_status_codes = self.reasons_for_unavailable_status_codes(stream, logger, source, error)
        known_reason = known_status_codes.get(status_code)
        if not known_reason:
            # If the HTTPError is not in the dictionary of errors we know how to handle, don't except
            raise error

        doc_ref = self._visit_docs_message(logger, source)
        reason = f"The endpoint {error.request_info.url} returned {status_code}: {error.message}. {known_reason}. {doc_ref} "
        return False, reason

    def reasons_for_unavailable_status_codes(
        self, stream: AsyncStream, logger: logging.Logger, source: Optional["Source"], error: ClientResponseError
    ) -> Dict[int, str]:
        """
        Returns a dictionary of HTTP status codes that indicate stream
        unavailability and reasons explaining why a given status code may
        have occurred and how the user can resolve that error, if applicable.

        :param stream: stream
        :param logger: source logger
        :param source: optional (source)
        :return: A dictionary of (status code, reason) where the 'reason' explains
        why 'status code' may have occurred and how the user can resolve that
        error, if applicable.
        """
        reasons_for_codes: Dict[int, str] = {
            requests.codes.FORBIDDEN: "This is most likely due to insufficient permissions on the credentials in use. "
            "Try to grant required permissions/scopes or re-authenticate"
        }
        return reasons_for_codes
