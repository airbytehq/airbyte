#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from airbyte_cdk.sources.async_cdk.abstract_source_async import AsyncAbstractSource
from airbyte_cdk.sources.async_cdk.streams.core_async import AsyncStream


class AsyncAvailabilityStrategy(ABC):
    """
    Abstract base class for checking stream availability.
    """

    @abstractmethod
    async def check_availability(
        self,
        stream: AsyncStream,
        logger: logging.Logger,
        source: Optional["AsyncAbstractSource"],
    ) -> Tuple[bool, Optional[str]]:
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
