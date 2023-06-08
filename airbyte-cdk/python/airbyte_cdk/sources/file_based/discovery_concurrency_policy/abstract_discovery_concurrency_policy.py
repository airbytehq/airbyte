#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC


class AbstractDiscoveryConcurrencyPolicy(ABC):
    """
    Used during discovery; allows the developer to configure the number of concurrent
    requests to send to the source.
    """

    n_concurrent_requests: int
