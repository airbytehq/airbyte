#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Optional

from pydantic.v1 import BaseModel


class FileRecordData(BaseModel):
    """
    A record in a file-based stream.
    """

    folder: str
    file_name: str
    bytes: int
    source_uri: str
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    mime_type: Optional[str] = None
