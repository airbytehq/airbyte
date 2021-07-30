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


import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Mapping

import pyarrow as pa
import pytest
from airbyte_cdk import AirbyteLogger
from smart_open import open as smart_open
from source_s3.source_files_abstract.fileformatparser import CsvParser, FileFormatParser

LOGGER = AirbyteLogger()
SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")


class TestFileFormatParserStatics:
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
        ],
    )
    def test_json_type_to_pyarrow_type(self, input_json_type, output_pyarrow_type):
        # Json -> PyArrow direction
        LOGGER.info(f"asserting that JSON type '{input_json_type}' converts to PyArrow type '{output_pyarrow_type}'...")
        assert FileFormatParser.json_type_to_pyarrow_type(input_json_type) == output_pyarrow_type

    @pytest.mark.parametrize(  # testing all datatypes as laid out here: https://arrow.apache.org/docs/python/api/datatypes.html
        "input_pyarrow_types, output_json_type",
        [
            ((pa.null(),), "string"),  # null type
            ((pa.bool_(),), "boolean"),  # boolean type
            (
                (pa.int8(), pa.int16(), pa.int32(), pa.int64(), pa.uint8(), pa.uint16(), pa.uint32(), pa.uint64()),
                "integer",
            ),  # integer types
            ((pa.float16(), pa.float32(), pa.float64(), pa.decimal128(5, 10), pa.decimal256(3, 8)), "number"),  # number types
            ((pa.time32("s"), pa.time64("ns"), pa.timestamp("ms"), pa.date32(), pa.date64()), "string"),  # temporal types
            ((pa.binary(), pa.large_binary()), "string"),  # binary types
            ((pa.string(), pa.utf8(), pa.large_string(), pa.large_utf8()), "string"),  # string types
            ((pa.list_(pa.string()), pa.large_list(pa.timestamp("us"))), "string"),  # array types
            ((pa.map_(pa.string(), pa.float32()), pa.dictionary(pa.int16(), pa.list_(pa.string()))), "string"),  # object types
        ],
    )
    def test_json_type_to_pyarrow_type_reverse(self, input_pyarrow_types, output_json_type):
        # PyArrow -> Json direction (reverse=True)
        for typ in input_pyarrow_types:
            LOGGER.info(f"asserting that PyArrow type '{typ}' converts to JSON type '{output_json_type}'...")
            assert FileFormatParser.json_type_to_pyarrow_type(typ, reverse=True) == output_json_type

    @pytest.mark.parametrize(  # if expecting fail, put pyarrow_schema as None
        "json_schema, pyarrow_schema",
        [
            (
                {"a": "string", "b": "number", "c": "integer", "d": "object", "e": "array", "f": "boolean", "g": "null"},
                {
                    "a": pa.large_string(),
                    "b": pa.float64(),
                    "c": pa.int64(),
                    "d": pa.large_string(),
                    "e": pa.large_string(),
                    "f": pa.bool_(),
                    "g": pa.large_string(),
                },
            ),
            ({"single_column": "object"}, {"single_column": pa.large_string()}),
            ({}, {}),
            ({"a": "NOT A REAL TYPE", "b": "another fake type"}, {"a": pa.large_string(), "b": pa.large_string()}),
            (["string", "object"], None),  # bad input type
        ],
    )
    def test_json_schema_to_pyarrow_schema(self, json_schema, pyarrow_schema):
        # Json -> PyArrow direction
        if pyarrow_schema is not None:
            assert FileFormatParser.json_schema_to_pyarrow_schema(json_schema) == pyarrow_schema
        else:
            with pytest.raises(Exception) as e_info:
                FileFormatParser.json_schema_to_pyarrow_schema(json_schema)
                LOGGER.debug(str(e_info))

    @pytest.mark.parametrize(  # if expecting fail, put json_schema as None
        "pyarrow_schema, json_schema",
        [
            (
                {
                    "a": pa.utf8(),
                    "b": pa.float16(),
                    "c": pa.uint32(),
                    "d": pa.map_(pa.string(), pa.float32()),
                    "e": pa.bool_(),
                    "f": pa.date64(),
                },
                {"a": "string", "b": "number", "c": "integer", "d": "string", "e": "boolean", "f": "string"},
            ),
            ({"single_column": pa.int32()}, {"single_column": "integer"}),
            ({}, {}),
            ({"a": "NOT A REAL TYPE", "b": "another fake type"}, {"a": "string", "b": "string"}),
            (["string", "object"], None),  # bad input type
        ],
    )
    def test_json_schema_to_pyarrow_schema_reverse(self, pyarrow_schema, json_schema):
        # PyArrow -> Json direction (reverse=True)
        if json_schema is not None:
            assert FileFormatParser.json_schema_to_pyarrow_schema(pyarrow_schema, reverse=True) == json_schema
        else:
            with pytest.raises(Exception) as e_info:
                FileFormatParser.json_schema_to_pyarrow_schema(pyarrow_schema, reverse=True)
                LOGGER.debug(str(e_info))


class AbstractTestFileFormatParser(ABC):
    """ Prefix this class with Abstract so the tests don't run here but only in the children """

    @property
    @abstractmethod
    def test_files(self) -> List[Mapping[str, Any]]:
        """return a list of test_file dicts in structure:
        [
            {"fileformatparser": CsvParser(format, master_schema), "filepath": "...", "num_records": 5, "inferred_schema": {...}, line_checks:{}, fails: []},
            {"fileformatparser": CsvParser(format, master_schema), "filepath": "...", "num_records": 16, "inferred_schema": {...}, line_checks:{}, fails: []}
        ]
        note: line_checks index is 1-based to align with row numbers
        """

    def _get_readmode(self, test_name, test_file):
        LOGGER.info(f"testing {test_name}() with {test_file.get('test_alias', test_file['filepath'].split('/')[-1])} ...")
        return "rb" if test_file["fileformatparser"].is_binary else "r"

    def test_get_inferred_schema(self):
        for test_file in self.test_files:
            with smart_open(test_file["filepath"], self._get_readmode("get_inferred_schema", test_file)) as f:
                if "test_get_inferred_schema" in test_file["fails"]:
                    with pytest.raises(Exception) as e_info:
                        test_file["fileformatparser"].get_inferred_schema(f)
                        LOGGER.debug(str(e_info))
                else:
                    assert test_file["fileformatparser"].get_inferred_schema(f) == test_file["inferred_schema"]

    def test_stream_records(self):
        for test_file in self.test_files:
            with smart_open(test_file["filepath"], self._get_readmode("stream_records", test_file)) as f:
                if "test_stream_records" in test_file["fails"]:
                    with pytest.raises(Exception) as e_info:
                        [print(r) for r in test_file["fileformatparser"].stream_records(f)]
                        LOGGER.debug(str(e_info))
                else:
                    records = [r for r in test_file["fileformatparser"].stream_records(f)]
                    assert len(records) == test_file["num_records"]
                    for index, expected_record in test_file["line_checks"].items():
                        assert records[index - 1] == expected_record


class TestCsvParser(AbstractTestFileFormatParser):
    @property
    def test_files(self) -> List[Mapping[str, Any]]:
        return [
            {
                # basic 'normal' test
                "fileformatparser": CsvParser(
                    format={"filetype": "csv"},
                    master_schema={
                        "id": "integer",
                        "name": "string",
                        "valid": "boolean",
                        "code": "integer",
                        "degrees": "number",
                        "birthday": "string",
                        "last_seen": "string",
                    },
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_1.csv"),
                "num_records": 8,
                "inferred_schema": {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
                "line_checks": {},
                "fails": [],
            },
            {
                # tests custom CSV parameters (odd delimiter, quote_char, escape_char & newlines in values in the file)
                "test_alias": "custom csv parameters",
                "fileformatparser": CsvParser(
                    format={"filetype": "csv", "delimiter": "^", "quote_char": "|", "escape_char": "!", "newlines_in_values": True},
                    master_schema={
                        "id": "integer",
                        "name": "string",
                        "valid": "boolean",
                        "code": "integer",
                        "degrees": "number",
                        "birthday": "string",
                        "last_seen": "string",
                    },
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_2_params.csv"),
                "num_records": 8,
                "inferred_schema": {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
                "line_checks": {},
                "fails": [],
            },
            {
                # tests encoding: Big5
                "test_alias": "encoding: Big5",
                "fileformatparser": CsvParser(
                    format={"filetype": "csv", "encoding": "big5"}, master_schema={"id": "integer", "name": "string", "valid": "boolean"}
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_3_enc_Big5.csv"),
                "num_records": 8,
                "inferred_schema": {"id": "integer", "name": "string", "valid": "boolean"},
                "line_checks": {
                    3: {
                        "id": 3,
                        "name": "變形金剛，偽裝的機器人",
                        "valid": False,
                    }
                },
                "fails": [],
            },
            {
                # tests encoding: Arabic (Windows 1256)
                "test_alias": "encoding: Arabic (Windows 1256)",
                "fileformatparser": CsvParser(
                    format={"filetype": "csv", "encoding": "windows-1256"},
                    master_schema={"id": "integer", "notes": "string", "valid": "boolean"},
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_4_enc_Arabic.csv"),
                "num_records": 2,
                "inferred_schema": {"id": "integer", "notes": "string", "valid": "boolean"},
                "line_checks": {
                    1: {
                        "id": 1,
                        "notes": "البايت الجوي هو الأفضل",
                        "valid": False,
                    }
                },
                "fails": [],
            },
            {
                # tests compression: gzip
                "test_alias": "compression: gzip",
                "fileformatparser": CsvParser(
                    format={"filetype": "csv"},
                    master_schema={
                        "id": "integer",
                        "name": "string",
                        "valid": "boolean",
                        "code": "integer",
                        "degrees": "number",
                        "birthday": "string",
                        "last_seen": "string",
                    },
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_5.csv.gz"),
                "num_records": 8,
                "inferred_schema": {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
                "line_checks": {
                    7: {
                        "id": 7,
                        "name": "xZhh1Kyl",
                        "valid": False,
                        "code": 10,
                        "degrees": -9.2,
                        "birthday": "2021-07-14",
                        "last_seen": "2021-07-14 15:30:09.225145",
                    }
                },
                "fails": [],
            },
            {
                # tests compression: bz2
                "test_alias": "compression: bz2",
                "fileformatparser": CsvParser(
                    format={"filetype": "csv"},
                    master_schema={
                        "id": "integer",
                        "name": "string",
                        "valid": "boolean",
                        "code": "integer",
                        "degrees": "number",
                        "birthday": "string",
                        "last_seen": "string",
                    },
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_7_bz2.csv.bz2"),
                "num_records": 8,
                "inferred_schema": {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
                "line_checks": {
                    7: {
                        "id": 7,
                        "name": "xZhh1Kyl",
                        "valid": False,
                        "code": 10,
                        "degrees": -9.2,
                        "birthday": "2021-07-14",
                        "last_seen": "2021-07-14 15:30:09.225145",
                    }
                },
                "fails": [],
            },
            {
                # tests extra columns in master schema
                "test_alias": "extra columns in master schema",
                "fileformatparser": CsvParser(
                    format={"filetype": "csv"},
                    master_schema={
                        "EXTRA_COLUMN_1": "boolean",
                        "EXTRA_COLUMN_2": "number",
                        "id": "integer",
                        "name": "string",
                        "valid": "boolean",
                        "code": "integer",
                        "degrees": "number",
                        "birthday": "string",
                        "last_seen": "string",
                    },
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_1.csv"),
                "num_records": 8,
                "inferred_schema": {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
                "line_checks": {},
                "fails": [],
            },
            {
                # tests missing columns in master schema
                # TODO: maybe this should fail read_records, but it does pick up all the columns from file despite missing from master schema
                "test_alias": "missing columns in master schema",
                "fileformatparser": CsvParser(format={"filetype": "csv"}, master_schema={"id": "integer", "name": "string"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_1.csv"),
                "num_records": 8,
                "inferred_schema": {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
                "line_checks": {},
                "fails": [],
            },
            {
                # tests empty file, SHOULD FAIL INFER & STREAM RECORDS
                "test_alias": "empty csv file",
                "fileformatparser": CsvParser(format={"filetype": "csv"}, master_schema={}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_6_empty.csv"),
                "num_records": 0,
                "inferred_schema": {},
                "line_checks": {},
                "fails": ["test_get_inferred_schema", "test_stream_records"],
            },
        ]
