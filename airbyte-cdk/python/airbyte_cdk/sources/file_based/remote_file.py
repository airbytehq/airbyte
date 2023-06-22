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
