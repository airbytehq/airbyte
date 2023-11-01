#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from io import IOBase
from typing import Iterable, List, Optional, Set

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import AbstractFileBasedSpec
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from wcmatch.glob import GLOBSTAR, globmatch


class FileReadMode(Enum):
    READ = "r"
    READ_BINARY = "rb"


class AbstractFileBasedStreamReader(ABC):
    DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self) -> None:
        self._config = None

    @property
    def config(self) -> Optional[AbstractFileBasedSpec]:
        return self._config

    @config.setter
    @abstractmethod
    def config(self, value: AbstractFileBasedSpec) -> None:
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        ...

    @abstractmethod
    def open_file(self, file: RemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
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
        prefix: Optional[str],
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

    def filter_files_by_globs_and_start_date(self, files: List[RemoteFile], globs: List[str]) -> Iterable[RemoteFile]:
        """
        Utility method for filtering files based on globs.
        """
        start_date = datetime.strptime(self.config.start_date, self.DATE_TIME_FORMAT) if self.config and self.config.start_date else None
        seen = set()

        for file in files:
            if self.file_matches_globs(file, globs):
                if file.uri not in seen and (not start_date or file.last_modified >= start_date):
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
