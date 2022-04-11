#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import os
import random
import string
import sys
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, List, Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from smart_open import open as smart_open
from source_files_abstract.utils import memory_limit


class AbstractTestParser(ABC):
    """Prefix this class with Abstract so the tests don't run here but only in the children"""

    logger = AirbyteLogger()
    record_types: Mapping[str, Any] = {}
    string_shuffle = [i for i in string.printable]

    def _generate_row(self, types: List[str]) -> List[Any]:
        """Generates random values with request types"""
        row = []
        for needed_type in types:
            for json_type in self.record_types:
                if json_type == needed_type:
                    row.append(self._generate_value(needed_type))
                    break
        return row

    def _generate_value(self, typ: str) -> Any:
        if typ not in ["boolean", "integer"] and self._generate_value("boolean"):
            # return 'None' for +- 33% of all requests
            return None

        if typ == "number":
            while True:
                int_value = self._generate_value("integer")
                if int_value:
                    break
            return float(int_value) + random.random()
        elif typ == "integer":
            return random.randint(-sys.maxsize - 1, sys.maxsize)
            # return random.randint(0, 1000)
        elif typ == "boolean":
            return random.choice([True, False, None])
        elif typ == "string":
            random_length = random.randint(0, 10 * 1024)  # max size of bytes is 10k
            random.shuffle(self.string_shuffle)
            rand_string = "".join("".join(self.string_shuffle).split())
            if random_length >= len(rand_string):
                multiplier = int(random_length / len(rand_string))
                rand_string = rand_string * multiplier
            else:
                rand_string = rand_string[:random_length]
            return rand_string
        elif typ == "timestamp":
            return datetime.now() + timedelta(seconds=random.randint(0, 7200))
        elif typ == "date":
            dt = self._generate_value("timestamp")
            return dt.date() if dt else None
        elif typ == "time":
            dt = self._generate_value("timestamp")
            return dt.time() if dt else None
        raise Exception(f"not supported type: {typ}")

    @lru_cache(maxsize=None)
    def cached_cases(self) -> Mapping[str, Any]:
        return self.cases()

    @abstractmethod
    def cases(self) -> Mapping[str, Any]:
        """return a map of test_file dicts in structure:
        {
           "small_file": {"AbstractFileParser": CsvParser(format, master_schema), "filepath": "...", "num_records": 5, "inferred_schema": {...}, line_checks:{}, fails: []},
           "big_file": {"AbstractFileParser": CsvParser(format, master_schema), "filepath": "...", "num_records": 16, "inferred_schema": {...}, line_checks:{}, fails: []}
        ]
        note: line_checks index is 1-based to align with row numbers
        """

    def _get_readmode(self, file_info: Mapping[str, Any]) -> str:
        return "rb" if file_info["AbstractFileParser"].is_binary else "r"

    @memory_limit(1024)
    def test_suite_inferred_schema(self, file_info: Mapping[str, Any]) -> None:
        with smart_open(file_info["filepath"], self._get_readmode(file_info)) as f:
            if "test_get_inferred_schema" in file_info["fails"]:
                with pytest.raises(Exception) as e_info:
                    file_info["AbstractFileParser"].get_inferred_schema(f)
                    self.logger.debug(str(e_info))
            else:
                assert file_info["AbstractFileParser"].get_inferred_schema(f) == file_info["inferred_schema"]

    @memory_limit(1024)
    def test_stream_suite_records(self, file_info: Mapping[str, Any]) -> None:
        filepath = file_info["filepath"]
        self.logger.info(f"read the file: {filepath}, size: {os.stat(filepath).st_size / (1024 ** 2)}Mb")
        with smart_open(filepath, self._get_readmode(file_info)) as f:
            if "test_stream_records" in file_info["fails"]:
                with pytest.raises(Exception) as e_info:
                    [print(r) for r in file_info["AbstractFileParser"].stream_records(f)]
                    self.logger.debug(str(e_info))
            else:
                records = [r for r in file_info["AbstractFileParser"].stream_records(f)]

                assert len(records) == file_info["num_records"]
                for index, expected_record in file_info["line_checks"].items():
                    assert records[index - 1] == expected_record
