#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy


class StripeSubStreamAvailabilityStrategy(HttpAvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """Traverse through all the parents of a given stream and run availability strategy on each of them"""
        try:
            current_stream, parent_stream = stream, getattr(stream, "parent")
        except AttributeError:
            return super().check_availability(stream, logger, source)
        if parent_stream:
            parent_stream_instance = getattr(current_stream, "get_parent_stream_instance")()
            # Accessing the `availability_strategy` property will instantiate AvailabilityStrategy under the hood
            availability_strategy = parent_stream_instance.availability_strategy
            if availability_strategy:
                is_available, reason = availability_strategy.check_availability(parent_stream_instance, logger, source)
                if not is_available:
                    return is_available, reason
        return super().check_availability(stream, logger, source)
