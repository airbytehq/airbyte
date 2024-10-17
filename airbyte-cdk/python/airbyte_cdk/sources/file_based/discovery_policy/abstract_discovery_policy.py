#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod

from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser


class AbstractDiscoveryPolicy(ABC):
    """
    Used during discovery; allows the developer to configure the number of concurrent
    requests to send to the source, and the number of files to use for schema discovery.
    """

    @property
    @abstractmethod
    def n_concurrent_requests(self) -> int:
        ...

    @abstractmethod
    def get_max_n_files_for_schema_inference(self, parser: FileTypeParser) -> int:
        ...
