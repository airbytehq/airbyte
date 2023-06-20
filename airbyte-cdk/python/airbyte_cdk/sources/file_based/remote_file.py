#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, Mapping

from pydantic import BaseModel


class RemoteFile(BaseModel):
    """
    A file in a file-based stream.
    """

    uri: str
    last_modified: datetime
    file_type: str

    @classmethod
    def from_file_partition(cls, file_partition: Mapping[str, Any]):
        return RemoteFile(uri=file_partition["uri"], last_modified=file_partition["last_modified"], file_type=file_partition["file_type"])
