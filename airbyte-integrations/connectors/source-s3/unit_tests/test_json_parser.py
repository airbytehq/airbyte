#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os
from pathlib import Path
from typing import Any, List, Mapping

import pytest
from source_s3.source_files_abstract.formats.json_parser import JsonParser

from .abstract_test_parser import AbstractTestParser

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")

test_files: List[Mapping[str, Any]] = [
    {
        # basic 'normal' test
        "test_alias": "basic_test",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_1.jsonl"),
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
        # tests custom JSON parameters (convert_dates, dtype)
        "test_alias": "custom json parameters",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json", "convert_dates": ["birthday"]},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_1.jsonl"),
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
        "AbstractFileParser": JsonParser(
            format={"filetype": "json", "encoding": "big5"}, master_schema={"id": "integer", "name": "string", "valid": "boolean"}
        ),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_2_enc_Big5.jsonl"),
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
        "AbstractFileParser": JsonParser(
            format={"filetype": "json", "encoding": "windows-1256"},
            master_schema={"id": "integer", "notes": "string", "valid": "boolean"},
        ),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_3_enc_Arabic.jsonl"),
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
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_4.jsonl.gz"),
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
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_5_bz2.jsonl.bz2"),
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
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_1.jsonl"),
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
        "AbstractFileParser": JsonParser(format={"filetype": "json"}, master_schema={"id": "integer", "name": "string"}),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_1.jsonl"),
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
        "test_alias": "empty json file",
        "AbstractFileParser": JsonParser(format={"filetype": "json"}, master_schema={}),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_6_empty.jsonl"),
        "num_records": 0,
        "inferred_schema": {},
        "line_checks": {},
        "fails": ["test_get_inferred_schema", "test_stream_records"],
    },
    {
        # tests file with differing schemas
        "test_alias": "json file with differing schemas",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_7_schema.jsonl"),
        "num_records": 8,
        "inferred_schema": {
            "id": "integer",
            "name": "string",
            "valid": "boolean",
            "code": "integer",
            "degrees": "number",
            "birthday": "string",
            "last_seen": "string",
            "creation_date": "string",
        },
        "line_checks": {},
        "fails": [],
    },
    {
        # tests file with nested objects and arrays
        "test_alias": "json file with nested objects and arrays",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
            master_schema={
                "id": "integer",
                "name": "string",
                "valid": "boolean",
                "code": "integer",
                "degrees": "number",
                "birthday": "string",
                "last_seen": "string",
                "location": "string",
                "categories": "string",
            },
        ),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_8_structures.jsonl"),
        "num_records": 8,
        "inferred_schema": {
            "id": "integer",
            "name": "string",
            "valid": "boolean",
            "code": "integer",
            "degrees": "number",
            "birthday": "string",
            "last_seen": "string",
            "location": "string",
            "categories": "string",
        },
        "line_checks": {},
        "fails": [],
    },
    {
        # tests file with datetimes
        "test_alias": "json file with datetimes",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
            master_schema={
                "id": "integer",
                "name": "string",
                "valid": "boolean",
                "code": "integer",
                "degrees": "number",
                "birthday": "string",
                "last_seen": "string",
                "date": "string",
                "timestamp": "string",
            },
        ),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_9_timestamp.jsonl"),
        "num_records": 8,
        "inferred_schema": {
            "id": "integer",
            "name": "string",
            "valid": "boolean",
            "code": "integer",
            "degrees": "number",
            "birthday": "string",
            "last_seen": "string",
            "date": "string",
            "timestamp": "string",
        },
        "line_checks": {},
        "fails": [],
    },
    {
        # tests that chunksize and nrows are taken into account
        "test_alias": "json file with chunk_size and nrows",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json", "chunk_size": 2, "nrows": 4},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_1.jsonl"),
        "num_records": 4,
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
        # tests that dtypes are taken into account
        "test_alias": "json file with schema",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json"},
            master_schema={
                "id": "integer",
                "name": "string",
                "valid": "boolean",
                "code": "number",
                "degrees": "number",
                "birthday": "string",
                "last_seen": "string",
            },
        ),
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_1.jsonl"),
        "num_records": 8,
        "inferred_schema": {
            "id": "integer",
            "name": "string",
            "valid": "boolean",
            "code": "number",
            "degrees": "number",
            "birthday": "string",
            "last_seen": "string",
        },
        "line_checks": {},
        "fails": [],
    },
    {
        # tests multiline json file
        "test_alias": "multiline json file",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json", "lines": False, "chunk_size": None},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_10_multiline.json"),
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
        # tests multiline json file
        "test_alias": "multiline json file",
        "AbstractFileParser": JsonParser(
            format={"filetype": "json", "lines": False, "chunk_size": None},
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
        "filepath": os.path.join(SAMPLE_DIRECTORY, "json/test_file_6_empty.jsonl"),
        "num_records": 0,
        "inferred_schema": {},
        "line_checks": {},
        "fails": ["test_get_inferred_schema", "test_stream_records"],
    },
]


@pytest.mark.parametrize("test_file", argvalues=test_files, ids=[file["test_alias"] for file in test_files])
class TestJsonParser(AbstractTestParser):
    @property
    def test_files(self) -> List[Mapping[str, Any]]:
        return test_files
