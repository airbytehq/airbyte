#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod


class AbstractDiscoveryPolicy(ABC):
    """
    Used during discovery; allows the developer to configure the number of concurrent
    requests to send to the source, and the number of files to use for schema discovery.
    """

    @property
    @abstractmethod
    def n_concurrent_requests(self) -> int:
        ...

    @property
    @abstractmethod
    def max_n_files_for_schema_inference(self) -> int:
        ...
