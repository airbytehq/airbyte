#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import BinaryIO, Iterator, TextIO, Union

from airbyte_cdk.logger import AirbyteLogger

from .file_info import FileInfo


class StorageFile(ABC):
    logger = AirbyteLogger()

    def __init__(self, file_info: FileInfo, provider: dict):
        """
        :param url: value yielded by filepath_iterator() in [Incremental]FileStream class. Blob/File path.
        :param provider: provider specific mapping as described in spec.json
        """
        self.file_info = file_info
        self._provider = provider

    @property
    def last_modified(self) -> datetime:
        """
        Returns last_modified property of the blob/file
        """
        return self.file_info.last_modified

    @property
    def file_size(self) -> int:
        """
        Returns Size property of the blob/file
        """
        return self.file_info.size

    @property
    def url(self) -> str:
        """
        Returns key/name files
        This function is needed for backward compatibility
        """
        return self.file_info.key

    @contextmanager
    @abstractmethod
    def open(self, binary: bool) -> Iterator[Union[TextIO, BinaryIO]]:
        """
        Override this to implement provider-specific logic.
        It should yield exactly one TextIO or BinaryIO, that being the opened file-like object.
        Note: This must work as described in https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager.
        Using contextmanager eliminates need to write all the boilerplate management code in this class.
        See S3File() for example implementation.

        :param binary: whether or not to open file as binary
        :return: file-like object
        """
