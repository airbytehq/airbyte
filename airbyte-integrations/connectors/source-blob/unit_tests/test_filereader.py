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


from abc import ABC, abstractmethod
import pyarrow as pa
import pytest
from source_blob.filereader import FileReader, FileReaderCsv
from airbyte_cdk import AirbyteLogger
from typing import List, Mapping, Any


logger = AirbyteLogger()


class TestFileReaderStatics():

    @pytest.mark.parametrize(  # testing all datatypes as laid out here: https://json-schema.org/understanding-json-schema/reference/type.html
        "input_json_type, output_pyarrow_type",
        [
            ("string", pa.large_string()),
            ("number", pa.float64()),
            ("integer", pa.int64()),
            ("object", pa.large_string()),
            ("array", pa.large_string()),
            ("boolean", pa.bool_()),
            ("null", pa.large_string()),
        ]
    )
    def test_json_type_to_pyarrow_type(self, input_json_type, output_pyarrow_type):
        # Json -> PyArrow direction
        logger.info(f"asserting that JSON type '{input_json_type}' converts to PyArrow type '{output_pyarrow_type}'...")
        assert FileReader.json_type_to_pyarrow_type(input_json_type) == output_pyarrow_type

    @pytest.mark.parametrize(  # testing all datatypes as laid out here: https://arrow.apache.org/docs/python/api/datatypes.html
        "input_pyarrow_types, output_json_type",
        [
            ((pa.null(), ), "string"),  # null type
            ((pa.bool_(), ), "boolean"),  # boolean type
            ((pa.int8(), pa.int16(), pa.int32(), pa.int64(), pa.uint8(), pa.uint16(), pa.uint32(), pa.uint64()), "integer"),  # integer types
            ((pa.float16(), pa.float32(), pa.float64(), pa.decimal128(5, 10), pa.decimal256(3, 8)), "number"),  # number types
            ((pa.time32("s"), pa.time64("ns"), pa.timestamp("ms"), pa.date32(), pa.date64()), "string"),  # temporal types
            ((pa.binary(), pa.large_binary()), "string"),  # binary types
            ((pa.string(), pa.utf8(), pa.large_string(), pa.large_utf8()), "string"),  # string types
            ((pa.list_(pa.string()), pa.large_list(pa.timestamp("us"))), "string"),  # array types
            ((pa.map_(pa.string(), pa.float32()), pa.dictionary(pa.int16(), pa.list_(pa.string()))), "string")  # object types
        ]
    )
    def test_json_type_to_pyarrow_type_reverse(self, input_pyarrow_types, output_json_type):

        # PyArrow -> Json direction (reverse=True)
        for typ in input_pyarrow_types:
            logger.info(f"asserting that PyArrow type '{typ}' converts to JSON type '{output_json_type}'...")
            assert FileReader.json_type_to_pyarrow_type(typ, reverse=True) == output_json_type

    @pytest.mark.parametrize(  # if expecting fail, put pyarrow_schema as None
        "json_schema, pyarrow_schema",
        [
            (
                {"a": "string", "b": "number", "c": "integer", "d": "object", "e": "array", "f": "boolean", "g": "null"},
                {"a": pa.large_string(), "b": pa.float64(), "c": pa.int64(), "d": pa.large_string(), "e": pa.large_string(), "f": pa.bool_(), "g": pa.large_string()}
            ),
            ({"single_column": "object"}, {"single_column": pa.large_string()}),
            ({}, {}),
            ({"a": "NOT A REAL TYPE", "b": "another fake type"}, {"a": pa.large_string(), "b": pa.large_string()}),
            (["string", "object"], None)  # wrong input type
        ]
    )
    def test_json_schema_to_pyarrow_schema(self, json_schema, pyarrow_schema):
        # Json -> PyArrow direction
        print(pyarrow_schema)
        if pyarrow_schema is not None:
            assert FileReader.json_schema_to_pyarrow_schema(json_schema) == pyarrow_schema
        else:
            with pytest.raises(Exception) as e_info:
                FileReader.json_schema_to_pyarrow_schema(json_schema)

        # PyArrow -> Json direction (reverse=True)


class AbstractTestFileReader(ABC):
    """ Prefix this class with Abstract so the tests don't run here but only in the children """

    @property
    @abstractmethod
    def test_files(self) -> List[Mapping[str,Any]]:
        """ return a list of test_file dicts in structure:
            [
                {"filereader": FileReaderCsv(format, master_schema), "filepath": "...", "num_records": 5, "inferred_schema": {...}},
                {"filereader": FileReaderCsv(format, master_schema), "filepath": "...", "num_records": 16, "inferred_schema": {...}}
            ]
        """

    def test_get_inferred_schema(self):
        for test_file in self.test_files:
            assert test_file("filereader").get_inferred_schema(test_file['filepath']) == test_file["inferred_schema"]


class TestFileReaderCsv(AbstractTestFileReader):

    @property
    def test_files(self) -> List[Mapping[str,Any]]:
        return [
            {
                "filereader": FileReaderCsv(format={"filetype": "csv"}),
                "filepath": "...",
                "num_records": 5,
                "inferred_schema": {}
            }
        ]

    def filereader_class(self):
        return FileReaderCsv
