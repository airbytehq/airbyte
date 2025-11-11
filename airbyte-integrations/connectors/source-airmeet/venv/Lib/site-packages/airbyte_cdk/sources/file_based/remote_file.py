#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from pydantic.v1 import BaseModel


class RemoteFile(BaseModel):
    """
    A file in a file-based stream.
    """

    uri: str
    last_modified: datetime
    mime_type: Optional[str] = None


class UploadableRemoteFile(RemoteFile, ABC):
    """
    A file in a file-based stream that supports uploading(file transferring).
    """

    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    @abstractmethod
    def size(self) -> int:
        """
        Returns the file size in bytes.
        """
        ...

    @abstractmethod
    def download_to_local_directory(self, local_file_path: str) -> None:
        """
        Download the file from remote source to local storage.
        """
        ...

    @property
    def source_file_relative_path(self) -> str:
        """
        Returns the relative path of the source file.
        """
        return self.uri

    @property
    def file_uri_for_logging(self) -> str:
        """
        Returns the URI for the file being logged.
        """
        return self.uri
