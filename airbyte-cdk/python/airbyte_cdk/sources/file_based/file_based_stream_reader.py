#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from io import IOBase
from typing import Iterable, List, Optional, Set, Generic

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.remote_file import FileReadMode, RemoteFile
from wcmatch.glob import GLOBSTAR, globmatch
from airbyte_cdk.sources.file_based.types import SpecType


class AbstractFileBasedStreamReader(ABC, Generic[SpecType]):
    def __init__(self) -> None:
        self._config = None

    @property
    def config(self) -> Optional[AbstractFileBasedSpec[SpecType]]:
        return self._config

    @config.setter
    @abstractmethod
    def config(self, value: AbstractFileBasedSpec[SpecType]) -> None:
        ...

    @abstractmethod
    def open_file(self, file: RemoteFile, mode: FileReadMode, logger: logging.Logger) -> IOBase:
        """
        Return a file handle for reading.

        Many sources will be able to use smart_open to implement this method,
        for example:

        client = boto3.Session(...)
        return smart_open.open(remote_file.uri, transport_params={"client": client})
        """
        ...

    @abstractmethod
    def get_matching_files(
        self,
        globs: List[str],
        logger: logging.Logger,
    ) -> Iterable[RemoteFile]:
        """
        Return all files that match any of the globs.

        Example:

        The source has files "a.json", "foo/a.json", "foo/bar/a.json"

        If globs = ["*.json"] then this method returns ["a.json"].

        If globs = ["foo/*.json"] then this method returns ["foo/a.json"].

        Utility method `self.filter_files_by_globs` and `self.get_prefixes_from_globs`
        are available, which may be helpful when implementing this method.
        """
        ...

    @classmethod
    def filter_files_by_globs(cls, files: List[RemoteFile], globs: List[str]) -> Iterable[RemoteFile]:
        """
        Utility method for filtering files based on globs.
        """
        seen = set()

        for file in files:
            if cls.file_matches_globs(file, globs):
                if file.uri not in seen:
                    seen.add(file.uri)
                    yield file

    @staticmethod
    def file_matches_globs(file: RemoteFile, globs: List[str]) -> bool:
        # Use the GLOBSTAR flag to enable recursive ** matching
        # (https://facelessuser.github.io/wcmatch/wcmatch/#globstar)
        return any(globmatch(file.uri, g, flags=GLOBSTAR) for g in globs)

    @staticmethod
    def get_prefixes_from_globs(globs: List[str]) -> Set[str]:
        """
        Utility method for extracting prefixes from the globs.
        """
        prefixes = {glob.split("*")[0] for glob in globs}
        return set(filter(lambda x: bool(x), prefixes))
