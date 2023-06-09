#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.discovery_concurrency_policy.abstract_discovery_concurrency_policy import (
    AbstractDiscoveryConcurrencyPolicy,
)


DEFAULT_N_CONCURRENT_REQUESTS = 10


class DefaultDiscoveryConcurrencyPolicy(AbstractDiscoveryConcurrencyPolicy):
    """
    Default number of concurrent requests to send to the source.
    """

    @property
    def n_concurrent_requests(self):
        return DEFAULT_N_CONCURRENT_REQUESTS
