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
from datetime import datetime
from typing import Union, TextIO, BinaryIO
from airbyte_cdk.logger import AirbyteLogger


class ConfigurationError(Exception):
    """Client mis-configured"""


class PermissionsError(Exception):
    """User doesn't have enough permissions"""


class FileClient(ABC):

    def __init__(self, url: str, provider: dict):
        """
        :param url: value yielded by filepath_iterator() in [Incremental]FileStream class. Blob/File path
        :type url: str
        :param provider: provider specific mapping as described in spec.json
        :type provider: dict
        """
        self._url = url
        self._provider = provider
        self._file = None
        self.logger = AirbyteLogger()

    def __enter__(self) -> Union[TextIO, BinaryIO]:
        """
        :return: file-like object
        :rtype: Union[TextIO, BinaryIO]
        """
        return self._file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def open(self, binary: bool=False):
        self.close()
        self._file = self._open(binary=binary)
        return self

    @property
    @abstractmethod
    def last_modified(self) -> datetime:
        """
        Override this to implement provider-specific logic

        :return: last_modified property of the blob/file
        :rtype: datetime
        """

    @abstractmethod
    def _open(self, binary: bool):
        """
        Override this to implement provider-specific logic

        :param binary: whether or not to open file as binary
        :type binary: bool
        """
