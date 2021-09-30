#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import BinaryIO, Iterator, TextIO, Union

from airbyte_cdk.logger import AirbyteLogger


class StorageFile(ABC):
    def __init__(self, url: str, provider: dict):
        """
        :param url: value yielded by filepath_iterator() in [Incremental]FileStream class. Blob/File path.
        :param provider: provider specific mapping as described in spec.json
        """
        self.url = url
        self._provider = provider
        self.logger = AirbyteLogger()

    @property
    @abstractmethod
    def last_modified(self) -> datetime:
        """
        Override this to implement provider-specific logic

        :return: last_modified property of the blob/file
        """

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
