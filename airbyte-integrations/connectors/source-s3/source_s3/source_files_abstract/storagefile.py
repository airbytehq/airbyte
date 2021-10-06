#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
