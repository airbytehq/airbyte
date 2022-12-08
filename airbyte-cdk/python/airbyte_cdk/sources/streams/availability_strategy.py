#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from airbyte_cdk.sources.streams import Stream

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class AvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability.
    """

    @abstractmethod
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """


class ScopedAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability based on required scopes for streams and
        the scopes granted to the source.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is returned. Otherwise, the stream is unavailable
          due to missing scopes, and the str tells the user which scopes are missing.
        """
        required_scopes_for_stream = self.required_scopes(stream, logger, source)
        granted_scopes = self.get_granted_scopes(stream, logger, source)
        if all([scope in granted_scopes for scope in required_scopes_for_stream]):
            return True, None
        else:
            missing_scopes = [scope for scope in required_scopes_for_stream if scope not in granted_scopes]
            error_message = f"Missing required scopes: {missing_scopes} for stream {stream.name}. Granted scopes: {granted_scopes}"
            return False, error_message

    @abstractmethod
    def get_granted_scopes(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> List[str]:
        """
        Returns scopes granted to the user.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :return: A list of scopes granted to the user.
        """

    @abstractmethod
    def required_scopes(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> List[str]:
        """
        Returns scopes required to access the stream.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :return: A list of scopes required to access the stream.
        """
