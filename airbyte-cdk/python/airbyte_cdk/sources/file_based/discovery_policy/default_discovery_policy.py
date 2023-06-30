#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.discovery_policy.abstract_discovery_policy import AbstractDiscoveryPolicy

DEFAULT_N_CONCURRENT_REQUESTS = 10
DEFAULT_MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE = 10


class DefaultDiscoveryPolicy(AbstractDiscoveryPolicy):
    """
    Default number of concurrent requests to send to the source on discover, and number
    of files to use for schema inference.
    """

    @property
    def n_concurrent_requests(self) -> int:
        return DEFAULT_N_CONCURRENT_REQUESTS

    @property
    def max_n_files_for_schema_inference(self) -> int:
        return DEFAULT_MAX_N_FILES_FOR_STREAM_SCHEMA_INFERENCE
