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
from pathlib import Path
from typing import Any, List, Mapping

from source_s3.source_files_abstract.formats.csv_parser import CsvParser

from .abstract_test_parser import AbstractTestParser

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")


class TestCsvParser(AbstractTestParser):
    @property
    def test_files(self) -> List[Mapping[str, Any]]:
        return [
            {
                # basic 'normal' test
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(
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
                "AbstractFileParser": CsvParser(format={"filetype": "csv"}, master_schema={"id": "integer", "name": "string"}),
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
                "AbstractFileParser": CsvParser(format={"filetype": "csv"}, master_schema={}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_6_empty.csv"),
                "num_records": 0,
                "inferred_schema": {},
                "line_checks": {},
                "fails": ["test_get_inferred_schema", "test_stream_records"],
            },
        ]
