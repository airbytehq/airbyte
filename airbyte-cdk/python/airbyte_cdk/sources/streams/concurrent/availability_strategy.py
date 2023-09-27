#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from deprecated.classic import deprecated


@deprecated("This class is experimental. Use at your own risk.")
class AbstractAvailabilityStrategy(ABC):
    """
    AbstractAvailabilityStrategy is an experimental interface developed as part of the Concurrent CDK.
    This interface is not yet stable and may change in the future. Use at your own risk.

    Why create a new interface instead of using the existing AvailabilityStrategy?
    The existing AvailabilityStrategy is tightly coupled with Stream and Source, which yields to circular dependencies and makes it difficult to move away from the Stream interface to AbstractStream.
    """

    @abstractmethod
    def check_availability(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        :param logger: logger object to use
        :return: A tuple of (boolean, str). If boolean is true, then the stream
          is available, and no str is required. Otherwise, the stream is unavailable
          for some reason and the str should describe what went wrong and how to
          resolve the unavailability, if possible.
        """


@deprecated("This class is experimental. Use at your own risk.")
class LegacyAvailabilityStrategy(AbstractAvailabilityStrategy):
    """
    This class acts as an adapter between the existing AvailabilityStrategy and the new AbstractAvailabilityStrategy.
    LegacyAvailabilityStrategy is instantiated with a Stream and a Source to allow the existing AvailabilityStrategy to be used with the new AbstractAvailabilityStrategy interface.

    This class can be used to help enable concurrency on existing connectors without having to rewrite everything as AbstractStream and AbstractAvailabilityStrategy.
    In the long-run, it would be preferable to update the connectors, but we don't have the tooling or need to justify the effort at this time.
    """

    def __init__(self, stream: Stream, source: Source):
        self._stream = stream
        self._source = source

    def check_availability(self, logger: logging.Logger) -> Tuple[bool, Optional[str]]:
        return self._stream.check_availability(logger, self._source)


@deprecated("This class is experimental. Use at your own risk.")
class AvailabilityStrategyFacade(AvailabilityStrategy):
    """
    The AvailabilityStrategyFacade is a AvailabilityStrategy that wraps an AbstractAvailabilityStrategy and exposes it as a AvailabilityStrategy.

    All methods delegate to the underlying AbstractAvailabilityStrategy.
    """

    def __init__(self, abstract_availability_strategy: AbstractAvailabilityStrategy):
        self._abstract_availability_strategy = abstract_availability_strategy

    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """
        Checks stream availability.

        Important to note that the stream and source parameters are not used by the underlying AbstractAvailabilityStrategy.

        :param stream: (unused)
        :param logger: logger object to use
        :param source: (unused)
        :return: A tuple of (boolean, str). If boolean is true, then the stream
        """
        return self._abstract_availability_strategy.check_availability(logger)
