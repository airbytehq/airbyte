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
        while parent_stream:
            # 1. Instantiate a parent stream
            # 2. Run availability strategy of the parent stream if specified
            # 3. Switch to parent of the parent
            parent_stream_instance = getattr(current_stream, "get_parent_stream_instance")()
            # Accessing the `availability_strategy` property will instantiate AvailabilityStrategy under the hood
            availability_strategy = parent_stream_instance.availability_strategy
            if availability_strategy:
                available, reason = availability_strategy.check_availability(parent_stream_instance, logger, source)
                if not available:
                    return available, reason
            if not hasattr(parent_stream, "parent"):
                break
            current_stream, parent_stream = parent_stream, getattr(parent_stream, "parent")
        # Finally check whether given stream is available
        return super().check_availability(stream, logger, source)
