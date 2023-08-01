#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RemoteFile(BaseModel):
    """
    A file in a file-based stream.
    """

    uri: str
    last_modified: datetime

    def extension_agrees_with_file_type(self, file_type: Optional[str]) -> bool:
        extensions = self.uri.split(".")[1:]
        if not extensions:
            return True
        if not file_type:
            return True
        return any(file_type.casefold() in e.casefold() for e in extensions)
