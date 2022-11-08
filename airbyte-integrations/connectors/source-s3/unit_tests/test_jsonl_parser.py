#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
from pathlib import Path
from typing import Any, Mapping

from source_s3.source_files_abstract.formats.jsonl_parser import JsonlParser

from .abstract_test_parser import AbstractTestParser

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")


class TestJsonlParser(AbstractTestParser):
    @classmethod
    def cases(cls) -> Mapping[str, Any]:
        return {
            "basic_normal_test": {
                "AbstractFileParser": JsonlParser(format={"filetype": "jsonl"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_1.jsonl"),
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
            "master_schema_test": {
                "AbstractFileParser": JsonlParser(
                    format={"filetype": "jsonl"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_1.jsonl"),
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
            "encoding_Big5": {
                "AbstractFileParser": JsonlParser(format={"filetype": "jsonl"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_2_enc_Big5.jsonl"),
                "num_records": 8,
                "inferred_schema": {"id": "integer", "name": "string", "valid": "boolean"},
                "line_checks": {},
                "fails": [],
            },
            "encoding_Arabic_(Windows 1256)": {
                "AbstractFileParser": JsonlParser(format={"filetype": "jsonl"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_3_enc_Arabic.jsonl"),
                "num_records": 2,
                "inferred_schema": {"id": "integer", "notes": "string", "valid": "boolean"},
                "line_checks": {},
                "fails": [],
            },
            "compression_gz": {
                "AbstractFileParser": JsonlParser(
                    format={"filetype": "jsonl"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_4.jsonl.gz"),
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
            "extra_columns_in_master_schema": {
                # tests extra columns in master schema
                "AbstractFileParser": JsonlParser(
                    format={"filetype": "jsonl"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_1.jsonl"),
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
            "missing_columns_in_master_schema": {
                # tests missing columns in master schema
                "AbstractFileParser": JsonlParser(format={"filetype": "jsonl"}, master_schema={"id": "integer", "name": "string"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_1.jsonl"),
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
            "nested_json_test": {
                "AbstractFileParser": JsonlParser(format={"filetype": "jsonl"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_10_nested_structure.jsonl"),
                "num_records": 2,
                "inferred_schema": {"meta": "object", "payload": "object"},
                "line_checks": {},
                "fails": [],
            },
            "array_in_schema_test": {
                "AbstractFileParser": JsonlParser(format={"filetype": "jsonl"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "jsonl/test_file_11_array_in_schema.jsonl"),
                "num_records": 3,
                "inferred_schema": {"id": "integer", "name": "string", "books": "array"},
                "line_checks": {},
                "fails": [],
            },
        }
