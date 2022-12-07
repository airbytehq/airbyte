#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Text, Tuple

from airbyte_cdk.sources.streams import Stream


class AvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability
    """

    @abstractmethod
    def check_availability(self, logger: logging.Logger, stream: Stream) -> Tuple[bool, any]:
        """
        Checks stream availability.

        :param source: source
        :param logger: source logger
        :param stream: stream
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available. Otherwise, the stream is unavailable for some reason and
          the str should describe what went wrong.
        """


class ScopedAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, logger: logging.Logger, stream: Stream) -> Tuple[bool, Optional[str]]:
        """
        Check stream availability based on required scopes for streams and
        the scopes granted to the source.

        :param source: source
        :param logger: source logger
        :param stream: stream
        :return: A tuple of (boolean, str). If boolean is true, then the strpeam
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
