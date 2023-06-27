#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.file_based.discovery_policy import DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy


class LowInferenceLimitDiscoveryPolicy(DefaultDiscoveryPolicy):
    @property
    def max_n_files_for_schema_inference(self):
        return 1


class DefaultTestAvailabilityStrategy(AvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, _: Optional[Source]) -> Tuple[bool, Optional[str]]:
        return True, None


def make_remote_files(files: List[str]) -> List[RemoteFile]:
    return [
        RemoteFile(f, datetime.strptime("2023-06-05T03:54:07.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"))
        for f in files
    ]
