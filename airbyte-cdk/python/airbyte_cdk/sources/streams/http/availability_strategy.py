#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from typing import Dict, Optional, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from requests import HTTPError

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class HttpAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
        """
        Check stream availability by attempting to read the first record of the
        stream.

        :param source: source
        :param logger: source logger
        :param stream: stream
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """
        try:
            # Some streams need a stream slice to read records (e.g. if they have a SubstreamSlicer)
            stream_slice = self._get_stream_slice(stream)
            records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            next(records)
        except HTTPError as error:
            return self.handle_http_error(stream, logger, source, error)
        return True, None

    def _get_stream_slice(self, stream):
        # We wrap the return output of stream_slices() because some implementations return types that are iterable,
        # but not iterators such as lists or tuples
        slices = iter(
            stream.stream_slices(
                cursor_field=stream.cursor_field,
                sync_mode=SyncMode.full_refresh,
            )
        )
        try:
            return next(slices)
        except StopIteration:
            return {}

    def handle_http_error(self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError):
        """
        Override this method to define error handling for various `HTTPError`s
        that are raised while attempting to check a stream's availability.

        Checks whether an error's status_code is in a list of unavailable_error_codes,
        and gets the associated reason for that error.

        :param stream: stream
        :param logger: source logger
        :param source: source
        :param error: HTTPError raised while checking stream's availability.
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """
        try:
            status_code = error.response.status_code
            reason = self.reasons_for_unavailable_status_codes(stream, logger, source)[status_code]
            return False, reason
        except KeyError:
            return True, None

    def reasons_for_unavailable_status_codes(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> Dict[int, str]:
        """
        Returns a dictionary of (status code, reason) where the 'reason' explains
        why that error code may have occurred and how the user can resolve that
        error, if applicable. Should return reasons for all errors listed in
        self.unavailable_error_codes.

        :param stream:
        :param logger:
        :param source:
        :return:
        """
        forbidden_error_message = f"The endpoint to access stream '{stream.name}' returned 403: Forbidden. "
        forbidden_error_message += "This is most likely due to insufficient permissions on the credentials in use. "
        forbidden_error_message += self._visit_docs_message(logger, source)

        reasons_for_codes: Dict[int, str] = {403: forbidden_error_message}
        return reasons_for_codes

    @staticmethod
    def _visit_docs_message(logger: logging.Logger, source: Optional["Source"]) -> str:
        """
        :param source:
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
        except FileNotFoundError:  # If we are unit testing without implementing spec()
            docs_url = "https://docs.airbyte.com/integrations/sources/test"
            return f"Please visit {docs_url} to learn more."
