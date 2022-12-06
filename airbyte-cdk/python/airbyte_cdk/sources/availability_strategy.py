#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import typing

import requests
from abc import ABC, abstractmethod
from requests import HTTPError
from typing import Dict, List, Optional, Text, Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams import Stream

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class AvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability
    """

    @abstractmethod
    def check_availability(self, source: "Source", logger: logging.Logger, stream: Stream) -> Tuple[bool, any]:
        """
        Checks stream availability.

        :param source: source
        :param logger: source logger
        :param stream: stream
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """


class HTTPAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, source: "Source", logger: logging.Logger, stream: Stream) -> Tuple[bool, str]:
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
            return self.handle_http_error(source, logger, stream, error)
        return True, None

    def handle_http_error(self, source: "Source", logger: logging.Logger, stream: Stream, error: HTTPError):
        """
        Override this method to define error handling for various `HTTPError`s
        that are raised while attempting to check a stream's availability.

        :param source: source
        :param logger: source logger
        :param stream: stream
        :param error: HTTPerror raised while checking stream's availability.
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """
        if error.response.status_code == requests.codes.FORBIDDEN:
            error_message = "This is most likely due to insufficient permissions on the credentials in use. "
            error_message += self._visit_docs_message(source, logger)
            return False, error_message

        error_message = repr(error)
        return False, error_message

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

    def _visit_docs_message(self, source: "Source", logger: logging.Logger) -> str:
        """
        :param source:
        :return: A message telling the user where to go to learn more about the source.
        """
        try:
            connector_spec = source.spec(logger)
            docs_url = connector_spec.documentationUrl
            if docs_url:
                learn_more_message = f"Please visit {docs_url} to learn more. "
            else:
                learn_more_message = "Please visit the connector's documentation to learn more. "

        except FileNotFoundError:  # If we are unit testing without implementing spec()
            docs_url = "https://docs.airbyte.com/integrations/sources/test"
            learn_more_message = f"Please visit {docs_url} to learn more."

        return learn_more_message


class ScopedAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, source: "Source", logger: logging.Logger, stream: Stream) -> Tuple[bool, Optional[str]]:
        """
        Check stream availability based on required scopes for streams and
        the scopes granted to the source.

        :param source: source
        :param logger: source logger
        :param stream: stream
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """
        required_scopes_for_stream = self.required_scopes()[stream.name]
        granted_scopes = self.get_granted_scopes()
        if all([scope in granted_scopes for scope in required_scopes_for_stream]):
            return True, None
        else:
            missing_scopes = [scope for scope in required_scopes_for_stream if scope not in granted_scopes]
            error_message = f"Missing required scopes: {missing_scopes} for stream {stream.name}. Granted scopes: {granted_scopes}"
            return False, error_message

    @abstractmethod
    def get_granted_scopes(self) -> List[Text]:
        """
        :return: A list of scopes granted to the user.
        """

    @abstractmethod
    def required_scopes(self) -> Dict[Text, List[Text]]:
        """
        :return: A dict of (stream name: list of required scopes). Should contain
        at minimum all streams defined in self.streams.
        """
