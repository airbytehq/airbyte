#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import os
from pathlib import Path
from typing import Any, Mapping

from source_s3.source_files_abstract.formats.json_parser import JsonParser

from .abstract_test_parser import AbstractTestParser

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")


class TestJsonParser(AbstractTestParser):
    @classmethod
    def cases(cls) -> Mapping[str, Any]:
        return {
            "basic_normal_test": {
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
            }
        }
