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
from os import read, uname
from typing import Iterator

from airbyte_cdk.logger import AirbyteLogger
import pyarrow as pa
from pyarrow import csv as pacsv


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
    def stream_records(self, file, skip_data=False) -> Iterator:
        """load and return the appropriate pandas dataframe.

        :param file: file-like object to read from
        :param skip_data: limit reading data
        :return: a generator of dataframes loaded from file
        """

    @staticmethod
    def json_type_to_pyarrow_type(typ, reverse=False):
        """Convert Airbyte Type to PyArrow types to (or the other way around if reverse=True)
        TODO: Docstring
        """
        str_typ = str(typ)
        # this is a map of airbyte types to pyarrow types. The first list element of the pyarrow types should be the one to use where required.
        map = {
            "boolean": ("bool_", "bool"),
            "integer": ("int64", "int8", "int16", "int32", "uint8", "uint16", "uint32", "uint64"),
            "number": ("float64", "float16", "float32", "decimal128", "decimal256", "halffloat", "float", "double"),
            "string": ("large_string", ),
            "object": ("large_string", ),
            "array": ("large_string", ),
            "null": ("large_string", )
        }
        if not reverse:
            for json_type, pyarrow_types in map.items():
                if str_typ == json_type:
                    return getattr(pa, pyarrow_types[0]).__call__()  # better way might be necessary when we decide to handle more type complexity
        else:
            for json_type, pyarrow_types in map.items():
                if any([str_typ.startswith(pa_type) for pa_type in pyarrow_types]):
                    return json_type
            return "string"  # default type if unspecified in map

    @staticmethod
    def json_schema_to_pyarrow_schema(schema, reverse=False):
        """ TODO docstring """
        new_schema = {}

        for column, json_type in schema.items():
            new_schema[column] = FileReader.json_type_to_pyarrow_type(json_type, reverse=reverse)

        return new_schema


class FileReaderCsv(FileReader):
    """  TODO Docstring """
    pass

    @property
    def is_binary(self):
        return True

    @property
    def read_options(self):
        return pa.csv.ReadOptions(
            block_size=10000,
            encoding=self._format.get("encoding", 'utf8')
        )

    @property
    def parse_options(self):
        return pa.csv.ParseOptions(
            delimiter=self._format.get("delimiter", ','),
            quote_char=self._format.get("quote_char", '"'),
            double_quote=self._format.get("double_quote", True),
            escape_char=self._format.get("escape_char", False),
            newlines_in_values=self._format.get("newlines_in_values", False)
        )

    @property
    def convert_options(self):
        check_utf8 = True if self._format.get("encoding", 'utf8').lower().replace("-", "") == 'utf8' else False
        return pa.csv.ConvertOptions(
            check_utf8=check_utf8,
            column_types=self.json_schema_to_pyarrow_schema(self._schema),
            **json.loads(self._format.get("additional_reader_options", '{}'))
        )

    def stream_records(self, file) -> Iterator:
        streaming_reader = pacsv.open_csv(file, self.read_options, self.parse_options, self.convert_options)
        still_reading = True
        while still_reading:
            try:
                batch = streaming_reader.read_next_batch().to_pydict()
            except StopIteration:
                still_reading = False
            else:
                for record_values in zip(*[batch[column] for column in self._schema.keys()]):
                    yield {list(self._schema.keys())[i]: record_values[i] for i in range(len(self._schema.keys()))}
