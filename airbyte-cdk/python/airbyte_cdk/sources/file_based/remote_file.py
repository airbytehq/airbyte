#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime
from typing import Any, Mapping


class RemoteFile(ABC):
    """
    A file in a file-based stream.
    """

    def __init__(self, uri: str, last_modified: datetime, file_type: str):
        self.uri = uri
        assert isinstance(last_modified, datetime)
        self.last_modified = last_modified
        self.file_type = file_type

    @classmethod
    def from_file_partition(cls, file_partition: Mapping[str, Any]):
        return RemoteFile(uri=file_partition["uri"],
                          last_modified=file_partition["last_modified"],
                          file_type=file_partition["file_type"])
