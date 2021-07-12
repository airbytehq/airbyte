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
from copy import deepcopy
import json
from os import read
from typing import Iterator

from airbyte_cdk.logger import AirbyteLogger
import pandas as pd


class FileReader(ABC):
    """ TODO docstring
    Manages parsing a tabular file. Child classes implement format specific logic (e.g. csv).
    """

    def __init__(self, format: dict, schema: dict):
        self._format = format
        self._schema = schema
        self.logger = AirbyteLogger()

    @property
    @abstractmethod
    def is_binary(self):
        """TODO docstring"""

    @property
    @abstractmethod
    def reader_options(self):
        """TODO docstring
        These should be defined in the spec.json per format 
        """

    @abstractmethod
    def stream_dataframes(self, file, skip_data=False) -> Iterator:
        """load and return the appropriate pandas dataframe.

        :param file: file-like object to read from
        :param skip_data: limit reading data
        :return: a generator of dataframes loaded from file
        """


class FileReaderCsv(FileReader):
    """  TODO Docstring """
    pass

    @property
    def is_binary(self):
        return False

    @property
    def reader_options(self):
        # init reader_options with system defaults
        reader_options = {'chunksize': 10000}  # TODO: make this configurable so user can attempt to optimise?
        # deal with specific user defined options
        options = ['sep', 'quotechar', 'escapechar', 'encoding']
        reader_options = {opt: self._format.get(opt) for opt in options if self._format.get(opt) is not None}
        # now parse and unpack any additional_reader_options
        if self._format.get("additional_reader_options") is not None:
            # TODO: clear error if the json.loads fails on the additional reader options provided
            reader_options = {**reader_options, **json.loads(self._format.get("additional_reader_options"))}

        return reader_options

    def stream_dataframes(self, file) -> Iterator:
        read_opts = deepcopy(self.reader_options)
        if skip_data:
            read_opts["nrows"] = 0
            read_opts["index_col"] = 0

        yield from pd.read_csv(file, **read_opts)
