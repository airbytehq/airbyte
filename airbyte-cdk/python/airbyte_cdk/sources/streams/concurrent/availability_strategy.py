#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class AbstractAvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability.
    """

    @abstractmethod
    def check_availability(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        :param logger: source logger
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """


class LegacyAvailabilityStrategy(AbstractAvailabilityStrategy):
    def __init__(self, stream: Stream, source: Source):
        self._stream = stream
        self._source = source

    def check_availability(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        return self._stream.availability_strategy.check_availability(self._stream, logger, self._source)


class ConcurrentAvailabilityStrategyAdapter(AvailabilityStrategy):
    def __init__(self, abstract_availability_strategy: AbstractAvailabilityStrategy):
        self._abstract_availability_strategy = abstract_availability_strategy

    def check_availability(self, stream: Stream, logger: logging.Logger, source) -> Tuple[bool, Optional[str]]:
        return self._abstract_availability_strategy.check_availability(logger)
