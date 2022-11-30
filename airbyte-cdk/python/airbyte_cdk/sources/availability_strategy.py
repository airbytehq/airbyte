#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from requests import HTTPError
from typing import Dict, List, Optional, Text, Tuple

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.streams import Stream


class AvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability
    """

    @abstractmethod
    def check_availability(self, stream: Stream) -> Tuple[bool, any]:
        """
        Checks stream availability.

        :param stream: stream
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """


class HTTPAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream) -> Tuple[bool, str]:
        """
        Check stream availability by attempting to read the first record of the
        stream.

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
            return False, repr(error)
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


class ScopedAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream) -> Tuple[bool, Optional[str]]:
        """
        Check stream availability based on required scopes for streams and
        the scopes granted to the source.

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
            return False, f"Missing required scopes: {missing_scopes} for stream {stream.name}. Granted scopes: {granted_scopes}"

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
