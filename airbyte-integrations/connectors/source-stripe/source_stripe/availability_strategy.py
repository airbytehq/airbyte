#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from requests import HTTPError

from .stream_helpers import get_first_record_for_slice, get_first_stream_slice

STRIPE_ERROR_CODES = {
    "more_permissions_required": "This is most likely due to insufficient permissions on the credentials in use. "
    "Try to grant required permissions/scopes or re-authenticate",
    "account_invalid": "The card, or account the card is connected to, is invalid. You need to contact your card issuer "
    "to check that the card is working correctly.",
    "oauth_not_supported": "Please use a different authentication method.",
}


class StripeAvailabilityStrategy(HttpAvailabilityStrategy):
    def _check_availability_for_sync_mode(
        self,
        stream: Stream,
        sync_mode: SyncMode,
        logger: logging.Logger,
        source: Optional["Source"],
        stream_state: Optional[Mapping[str, Any]],
    ) -> Tuple[bool, Optional[str]]:
        try:
            # Some streams need a stream slice to read records (e.g. if they have a SubstreamPartitionRouter)
            # Streams that don't need a stream slice will return `None` as their first stream slice.
            stream_slice = get_first_stream_slice(stream, sync_mode, stream_state)
        except StopIteration:
            # If stream_slices has no `next()` item (Note - this is different from stream_slices returning [None]!)
            # This can happen when a substream's `stream_slices` method does a `for record in parent_records: yield <something>`
            # without accounting for the case in which the parent stream is empty.
            reason = f"Cannot attempt to connect to stream {stream.name} - no stream slices were found, likely because the parent stream is empty."
            return False, reason
        except HTTPError as error:
            is_available, reason = self.handle_http_error(stream, logger, source, error)
            if not is_available:
                reason = f"Unable to get slices for {stream.name} stream, because of error in parent stream. {reason}"
            return is_available, reason

        try:
            get_first_record_for_slice(stream, sync_mode, stream_slice, stream_state)
            return True, None
        except StopIteration:
            logger.info(f"Successfully connected to stream {stream.name}, but got 0 records.")
            return True, None
        except HTTPError as error:
            is_available, reason = self.handle_http_error(stream, logger, source, error)
            if not is_available:
                reason = f"Unable to read {stream.name} stream. {reason}"
            return is_available, reason

    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
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
        is_available, reason = self._check_availability_for_sync_mode(stream, SyncMode.full_refresh, logger, source, None)
        if not is_available or not stream.supports_incremental:
            return is_available, reason
        return self._check_availability_for_sync_mode(stream, SyncMode.incremental, logger, source, {stream.cursor_field: 0})

    def handle_http_error(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
    ) -> Tuple[bool, Optional[str]]:
        status_code = error.response.status_code
        if status_code not in [400, 403]:
            raise error
        parsed_error = error.response.json()
        error_code = parsed_error.get("error", {}).get("code")
        error_message = STRIPE_ERROR_CODES.get(error_code, parsed_error.get("error", {}).get("message"))
        if not error_message:
            raise error
        doc_ref = self._visit_docs_message(logger, source)
        reason = f"The endpoint {error.response.url} returned {status_code}: {error.response.reason}. {error_message}. {doc_ref} "
        response_error_message = stream.parse_response_error_message(error.response)
        if response_error_message:
            reason += response_error_message
        return False, reason


class StripeSubStreamAvailabilityStrategy(StripeAvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """Traverse through all the parents of a given stream and run availability strategy on each of them"""
        try:
            current_stream, parent_stream = stream, getattr(stream, "parent")
        except AttributeError:
            return super().check_availability(stream, logger, source)
        if parent_stream:
            parent_stream_instance = getattr(current_stream, "parent")
            # Accessing the `availability_strategy` property will instantiate AvailabilityStrategy under the hood
            availability_strategy = parent_stream_instance.availability_strategy
            if availability_strategy:
                is_available, reason = availability_strategy.check_availability(parent_stream_instance, logger, source)
                if not is_available:
                    return is_available, reason
        return super().check_availability(stream, logger, source)
