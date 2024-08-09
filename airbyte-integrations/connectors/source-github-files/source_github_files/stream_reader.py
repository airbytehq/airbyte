#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import io
import json
import logging
import requests
from datetime import datetime
from io import IOBase
from typing import Iterable, List, Optional, Set

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.remote_file import RemoteFile

from .spec import SourceGithubFilesSpec


class GithubRemoteFile(RemoteFile):
    sha: str
    size: int  # size of file in bytes
    url: str  # to fetch contents


class SourceGithubFilesReader(AbstractFileBasedStreamReader):
    def __init__(self):
        super().__init__()

    @property
    def config(self) -> SourceGithubFilesSpec:
        return self._config

    @config.setter
    def config(self, value: SourceGithubFilesSpec):
        """
        FileBasedSource reads the config from disk and parses it, and once parsed, the source sets the config on its StreamReader.

        Note: FileBasedSource only requires the keys defined in the abstract config, whereas concrete implementations of StreamReader
        will require keys that (for example) allow it to authenticate with the 3rd party.

        Therefore, concrete implementations of AbstractFileBasedStreamReader's config setter should assert that `value` is of the correct
        config type for that type of StreamReader.
        """
        assert isinstance(value, SourceGithubFilesSpec)
        self._config = value

    def get_matching_files(self, globs: List[str], prefix: Optional[str], logger: logging.Logger) -> Iterable[RemoteFile]:
        """
        Get all files matching the specified glob patterns.
        """
        # TODO: used a public open source repo; take this from the authentication object later on
        owner = "Ishankoradia"
        repo = "LLD-concepts"
        branch = "main"

        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

        response = requests.request("GET", api_url, headers={}, data={})

        remote_files: list[RemoteFile] = []
        for file_res in response.json()["tree"]:
            if file_res["type"] == "blob":
                remote_file = GithubRemoteFile(
                    sha=file_res["sha"], size=file_res["size"], url=file_res["url"], last_modified=datetime.now(), uri=file_res["path"]
                )
                remote_files.append(remote_file)

        yield from self.filter_files_by_globs_and_start_date(remote_files, globs)

    def open_file(self, file: GithubRemoteFile, mode: FileReadMode, encoding: Optional[str], logger: logging.Logger) -> IOBase:
        # TODO
        pass
