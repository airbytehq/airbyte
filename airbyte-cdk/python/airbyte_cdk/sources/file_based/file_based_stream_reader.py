#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from datetime import datetime
from fnmatch import fnmatch
from io import IOBase
from typing import List, Optional

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from pydantic import BaseModel


class AbstractFileBasedStreamReader(BaseModel):
    @abstractmethod
    def open_file(self, file: RemoteFile) -> IOBase:
        """
        Return a file handle for reading.

        Many sources will be able to use smart_open to implement this method,
        for example:

        client = boto3.Session(...)
        return smart_open.open(remote_file.uri, transport_params={"client": client})
        """
        ...

    @abstractmethod
    def list_matching_files(
        self,
        globs: List[str],
        from_date: Optional[datetime] = None,
    ) -> List[RemoteFile]:
        """
        Return all files that match any of the globs. If a from_date provided,
        return only files last modified after that date.

        Example:

        The source has files "a.json", "foo/a.json", "foo/bar/a.json"

        If globs = ["*.json"] then this method returns ["a.json"].

        If globs = ["foo/*.json"] then this method returns ["foo/a.json"].

        Utility method `self.filter_files_by_globs` and `self.get_prefixes_from_globs`
        are available, which may be helpful when implementing this method.
        """
        ...

    @staticmethod
    def filter_files_by_globs(files: List[RemoteFile], globs: List[str]) -> List[RemoteFile]:
        """
        Utility method for filtering files based on globs.
        """
        return [file for file in files if any(fnmatch(file.uri, glob) for glob in globs)]

    @staticmethod
    def get_prefixes_from_globs(files: List[RemoteFile], globs: List[str]) -> List[str]:
        """
        Utility method for extracting prefixes from the globs.
        """
        ...
