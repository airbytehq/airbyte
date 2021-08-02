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

import json
from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Iterator, Mapping, TextIO, Union

import pyarrow as pa
from airbyte_cdk.logger import AirbyteLogger
from pyarrow import csv as pa_csv


class FileFormatParser(ABC):
    def __init__(self, format: dict, master_schema: dict = None):
        """
        :param format: file format specific mapping as described in spec.json
        :param master_schema: superset schema determined from all files, might be unused for some formats, defaults to None
        """
        self._format = format
        self._master_schema = (
            master_schema  # this may need to be used differently by some formats, pyarrow allows extra columns in csv schema
        )
        self.logger = AirbyteLogger()

    @property
    @abstractmethod
    def is_binary(self):
        """
        Override this per format so that file-like objects passed in are currently opened as binary or not
        """

    @abstractmethod
    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        Override this with format-specifc logic to infer the schema of file
        Note: needs to return inferred schema with JsonSchema datatypes

        :param file: file-like object (opened via StorageFile)
        :return: mapping of {columns:datatypes} where datatypes are JsonSchema types
        """

    @abstractmethod
    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        Override this with format-specifc logic to stream each data row from the file as a mapping of {columns:values}
        Note: avoid loading the whole file into memory to avoid OOM breakages

        :param file: file-like object (opened via StorageFile)
        :yield: data record as a mapping of {columns:values}
        """

    @staticmethod
    def json_type_to_pyarrow_type(typ: str, reverse: bool = False, logger: AirbyteLogger = AirbyteLogger()) -> str:
        """
        Converts Json Type to PyArrow types to (or the other way around if reverse=True)

        :param typ: Json type if reverse is False, else PyArrow type
        :param reverse: switch to True for PyArrow type -> Json type, defaults to False
        :param logger: defaults to AirbyteLogger()
        :return: PyArrow type if reverse is False, else Json type
        """
        str_typ = str(typ)
        # this is a map of airbyte types to pyarrow types. The first list element of the pyarrow types should be the one to use where required.
        map = {
            "boolean": ("bool_", "bool"),
            "integer": ("int64", "int8", "int16", "int32", "uint8", "uint16", "uint32", "uint64"),
            "number": ("float64", "float16", "float32", "decimal128", "decimal256", "halffloat", "float", "double"),
            "string": ("large_string", "string"),
            "object": ("large_string",),  # TODO: support object type rather than coercing to string
            "array": ("large_string",),  # TODO: support array type rather than coercing to string
            "null": ("large_string",),
        }
        if not reverse:
            for json_type, pyarrow_types in map.items():
                if str_typ.lower() == json_type:
                    return getattr(
                        pa, pyarrow_types[0]
                    ).__call__()  # better way might be necessary when we decide to handle more type complexity
            logger.debug(f"JSON type '{str_typ}' is not mapped, falling back to default conversion to large_string")
            return pa.large_string()
        else:
            for json_type, pyarrow_types in map.items():
                if any([str_typ.startswith(pa_type) for pa_type in pyarrow_types]):
                    return json_type
            logger.debug(f"PyArrow type '{str_typ}' is not mapped, falling back to default conversion to string")
            return "string"  # default type if unspecified in map

    @staticmethod
    def json_schema_to_pyarrow_schema(schema: Mapping[str, Any], reverse: bool = False) -> Mapping[str, Any]:
        """
        Converts a schema with JsonSchema datatypes to one with PyArrow types (or the other way if reverse=True)
        This utilises json_type_to_pyarrow_type() to convert each datatype

        :param schema: json/pyarrow schema to convert
        :param reverse: switch to True for PyArrow schema -> Json schema, defaults to False
        :return: converted schema dict
        """
        new_schema = {}

        for column, json_type in schema.items():
            new_schema[column] = FileFormatParser.json_type_to_pyarrow_type(json_type, reverse=reverse)

        return new_schema


class CsvParser(FileFormatParser):
    @property
    def is_binary(self):
        return True

    def _read_options(self):
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ReadOptions.html
        """
        return pa.csv.ReadOptions(block_size=10000, encoding=self._format.get("encoding", "utf8"))

    def _parse_options(self):
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ParseOptions.html
        """
        quote_char = self._format.get("quote_char", False) if self._format.get("quote_char", False) != "" else False
        return pa.csv.ParseOptions(
            delimiter=self._format.get("delimiter", ","),
            quote_char=quote_char,
            double_quote=self._format.get("double_quote", True),
            escape_char=self._format.get("escape_char", False),
            newlines_in_values=self._format.get("newlines_in_values", False),
        )

    def _convert_options(self, json_schema: Mapping[str, Any] = None):
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.ConvertOptions.html

        :param json_schema: if this is passed in, pyarrow will attempt to enforce this schema on read, defaults to None
        """
        check_utf8 = True if self._format.get("encoding", "utf8").lower().replace("-", "") == "utf8" else False
        convert_schema = self.json_schema_to_pyarrow_schema(json_schema) if json_schema is not None else None
        return pa.csv.ConvertOptions(
            check_utf8=check_utf8, column_types=convert_schema, **json.loads(self._format.get("additional_reader_options", "{}"))
        )

    def get_inferred_schema(self, file: Union[TextIO, BinaryIO]) -> dict:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.open_csv.html
        Note: this reads just the first block (as defined in _read_options() block_size) to infer the schema
        """
        streaming_reader = pa_csv.open_csv(file, self._read_options(), self._parse_options(), self._convert_options())
        schema_dict = {field.name: field.type for field in streaming_reader.schema}
        return self.json_schema_to_pyarrow_schema(schema_dict, reverse=True)

    def stream_records(self, file: Union[TextIO, BinaryIO]) -> Iterator[Mapping[str, Any]]:
        """
        https://arrow.apache.org/docs/python/generated/pyarrow.csv.open_csv.html
        PyArrow returns lists of values for each column so we zip() these up into records which we then yield
        """
        streaming_reader = pa_csv.open_csv(file, self._read_options(), self._parse_options(), self._convert_options(self._master_schema))
        still_reading = True
        while still_reading:
            try:
                batch = streaming_reader.read_next_batch()
            except StopIteration:
                still_reading = False
            else:
                batch_dict = batch.to_pydict()
                batch_columns = [col_info.name for col_info in batch.schema]
                # this gives us a list of lists where each nested list holds ordered values for a single column
                # e.g. [ [1,2,3], ["a", "b", "c"], [True, True, False] ]
                columnwise_record_values = [batch_dict[column] for column in batch_columns]
                # we zip this to get row-by-row, e.g. [ [1, "a", True], [2, "b", True], [3, "c", False] ]
                for record_values in zip(*columnwise_record_values):
                    # create our record of {col: value, col: value} by dict comprehension, iterating through all cols in batch_columns
                    yield {batch_columns[i]: record_values[i] for i in range(len(batch_columns))}
