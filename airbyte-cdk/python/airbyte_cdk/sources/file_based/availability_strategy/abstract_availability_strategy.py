#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import abstractmethod
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class AbstractFileBasedAvailabilityStrategy(AvailabilityStrategy):
    @abstractmethod
    def check_availability(self, stream: Stream, logger: logging.Logger, _: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """
        Perform a connection check for the stream.

        Returns (True, None) if successful, otherwise (False, <error message>).
        """
        ...
