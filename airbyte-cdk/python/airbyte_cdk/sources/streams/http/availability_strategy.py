#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from typing import Dict, Optional, Tuple

import requests
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.utils.stream_helper import get_first_record_for_slice, get_first_stream_slice
from requests import HTTPError

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class HttpAvailabilityStrategy(AvailabilityStrategy):
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
        try:
            # Some streams need a stream slice to read records (e.g. if they have a SubstreamPartitionRouter)
            # Streams that don't need a stream slice will return `None` as their first stream slice.
            stream_slice = get_first_stream_slice(stream)
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
            get_first_record_for_slice(stream, stream_slice)
            return True, None
        except StopIteration:
            logger.info(f"Successfully connected to stream {stream.name}, but got 0 records.")
            return True, None
        except HTTPError as error:
            is_available, reason = self.handle_http_error(stream, logger, source, error)
            if not is_available:
                reason = f"Unable to read {stream.name} stream. {reason}"
            return is_available, reason

    def handle_http_error(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
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
        status_code = error.response.status_code
        known_status_codes = self.reasons_for_unavailable_status_codes(stream, logger, source, error)
        known_reason = known_status_codes.get(status_code)
        if not known_reason:
            # If the HTTPError is not in the dictionary of errors we know how to handle, don't except
            raise error

        doc_ref = self._visit_docs_message(logger, source)
        reason = f"The endpoint {error.response.url} returned {status_code}: {error.response.reason}. {known_reason}. {doc_ref} "
        response_error_message = stream.parse_response_error_message(error.response)
        if response_error_message:
            reason += response_error_message
        return False, reason

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
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

    @staticmethod
    def _visit_docs_message(logger: logging.Logger, source: Optional["Source"]) -> str:
        """
        Creates a message indicating where to look in the documentation for
        more information on a given source by checking the spec of that source
        (if provided) for a 'documentationUrl'.

        :param logger: source logger
        :param source: optional (source)
        :return: A message telling the user where to go to learn more about the source.
        """
        if not source:
            return "Please visit the connector's documentation to learn more. "

        try:
            connector_spec = source.spec(logger)
            docs_url = connector_spec.documentationUrl
            if docs_url:
                return f"Please visit {docs_url} to learn more. "
            else:
                return "Please visit the connector's documentation to learn more. "

        except FileNotFoundError:  # If we are unit testing without implementing spec() method in source
            if source:
                docs_url = f"https://docs.airbyte.com/integrations/sources/{source.name}"
            else:
                docs_url = "https://docs.airbyte.com/integrations/sources/test"

            return f"Please visit {docs_url} to learn more."
