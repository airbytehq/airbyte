#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import typing
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Tuple

from airbyte_cdk.sources.streams import Stream

if typing.TYPE_CHECKING:
    from airbyte_cdk.sources import Source


class AvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability.
    """

    @abstractmethod
    def check_availability(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], stream_state: Optional[Mapping[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        :param stream: stream
        :param logger: source logger
        :param source: (optional) source
        :param stream_state: (optional) The stream state
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """
