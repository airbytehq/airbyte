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
import pyarrow as pa


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

    @abstractmethod
    def stream_dataframes(self, file, skip_data=False) -> Iterator:
        """load and return the appropriate pandas dataframe.

        :param file: file-like object to read from
        :param skip_data: limit reading data
        :return: a generator of dataframes loaded from file
        """

    @staticmethod
    def pyarrow_type_to_json_type(typ, reverse=False):
        """Convert PyArrow types to Airbyte Types (or the other way around if reverse=True)
        TODO: Docstring
        """
        typ = str(typ).lower()
        # this is a map of airbyte types to pyarrow types. The first list element of the pyarrow types should be the one to use where required.
        map = {  
            "boolean": ["bool"],
            "integer": ["int64", "int32"], 
            "int": "integer",
            "float": "number",
            "double": 1
        }
        # these types are just stubs as we'll do a .startswith check


class FileReaderCsv(FileReader):
    """  TODO Docstring """
    pass

    @property
    def is_binary(self):
        return False

    @property
    def read_options(self):
        return pa.csv.ReadOptions(
            block_size=10000,
            encoding=self._format.get("encoding", default='utf8')
        )

    @property
    def parse_options(self):
        return pa.csv.ParseOptions(
            delimiter=self._format.get("delimiter", default=','),
            quote_char=self._format.get("quote_char", default='"'),
            double_quote=self._format.get("double_quote", default=True),
            escape_char=self._format.get("escape_char", default=False),
            newlines_in_values=self._format.get("newlines_in_values", default=False)
        )

    @property
    def convert_options(self):
        check_utf8 = True if self._format.get("encoding", default='utf8').lower().replace("-", "") == 'utf8' else False
        return pa.csv.ConvertOptions(
            check_utf8=check_utf8,
            column_types=self._schema,
            **json.loads(self._format.get("additional_reader_options"))
        )


    def stream_dataframes(self, file) -> Iterator:
        # set variable defaults

        # init reader option dicts with airbyte defaults
        read_options = 
        headers = True
        if self._format.get("headers") is None
        reader_options = {'chunksize': 10000}  # TODO: make this configurable so user can attempt to optimise?
        # deal with specific user defined options
        options = ['sep', 'quotechar', 'escapechar', 'encoding']
        reader_options = {opt: self._format.get(opt) for opt in options if self._format.get(opt) is not None}
        # now parse and unpack any additional_reader_options
        if self._format.get("additional_reader_options") is not None:
            # TODO: clear error if the json.loads fails on the additional reader options provided
            reader_options = {**reader_options, **}