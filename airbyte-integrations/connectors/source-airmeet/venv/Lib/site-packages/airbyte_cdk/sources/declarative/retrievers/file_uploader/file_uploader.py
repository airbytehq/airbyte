#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass

from airbyte_cdk.sources.declarative.types import Record


@dataclass
class FileUploader(ABC):
    """
    Base class for file uploader
    """

    @abstractmethod
    def upload(self, record: Record) -> None:
        """
        Uploads the file to the specified location
        """
        ...
