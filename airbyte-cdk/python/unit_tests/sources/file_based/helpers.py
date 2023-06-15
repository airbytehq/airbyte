#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.discovery_policy import DefaultDiscoveryPolicy
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class LowInferenceLimitDiscoveryPolicy(DefaultDiscoveryPolicy):
    @property
    def max_n_files_for_schema_inference(self):
        return 1


class DefaultTestAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, _: Optional[Source]) -> Tuple[bool, Optional[str]]:
        return True, None
