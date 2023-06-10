#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.availability_strategy import AbstractFileBasedAvailabilityStrategy
from airbyte_cdk.sources.file_based.discovery_policy import DefaultDiscoveryPolicy
from airbyte_cdk.sources.streams import Stream


class LowInferenceLimitDiscoveryPolicy(DefaultDiscoveryPolicy):
    @property
    def max_n_files_for_schema_inference(self):
        return 1


class DefaultTestAvailabilityStrategy(AbstractFileBasedAvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, _: Optional[Source]) -> Tuple[bool, Optional[str]]:
        return True, None
