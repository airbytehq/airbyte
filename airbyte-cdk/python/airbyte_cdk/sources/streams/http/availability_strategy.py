#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from typing import Dict, Optional, Tuple

import requests
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.utils.stream_helpers import StreamHelper
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
            stream_helper = StreamHelper()
            stream_helper.get_first_record(stream)
        except HTTPError as error:
            return self.handle_http_error(stream, logger, source, error)
        return True, None

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
        try:
            status_code = error.response.status_code
            reason = self.reasons_for_unavailable_status_codes(stream, logger, source, error)[status_code]
            response_error_message = stream.parse_response_error_message(error.response)
            if response_error_message:
                reason += response_error_message
            return False, reason
        except KeyError:
            # If the HTTPError is not in the dictionary of errors we know how to handle, don't except it
            raise error

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
        forbidden_error_message = f"The endpoint to access stream '{stream.name}' returned 403: Forbidden. "
        forbidden_error_message += "This is most likely due to insufficient permissions on the credentials in use. "
        forbidden_error_message += self._visit_docs_message(logger, source)

        reasons_for_codes: Dict[int, str] = {requests.codes.FORBIDDEN: forbidden_error_message}
        return reasons_for_codes

    @staticmethod
    def _visit_docs_message(logger: logging.Logger, source: Optional["Source"]) -> str:
        """
        Creates a message indicicating where to look in the documentation for
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
