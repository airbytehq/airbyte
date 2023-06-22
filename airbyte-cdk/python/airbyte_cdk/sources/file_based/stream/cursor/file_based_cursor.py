#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping

from airbyte_cdk.sources.file_based.remote_file import RemoteFile


class FileBasedCursor(ABC):
    """
    Abstract base class for cursors used by file-based streams.
    """

    @abstractmethod
    def add_file(self, file: RemoteFile):
        """
        Add a file to the cursor. This method is called when a file is processed by the stream.
        :param file:
        :return:
        """
        ...

    @abstractmethod
    def get_state(self) -> Mapping[str, Any]:
        """
        Get the state of the cursor.
        :return:
        """
        ...
