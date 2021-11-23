#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, List, Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from smart_open import open as smart_open
import resource, os, psutil
from functools import wraps
from typing import Callable, List
import random
import sys
from datetime import datetime, timedelta
import shutil
from functools import lru_cache
from memory_profiler import memory_usage
import tempfile
import psutil
import pytest



def memory_limit(max_memory_in_megabytes: int) -> Callable:
    """Runs a test function by a separate process with restricted memory"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            total_used_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            used_memory, result = memory_usage((func, args, kwargs), max_usage=True, retval=True)
            used_memory = used_memory - total_used_memory
            total_used_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            assert used_memory < max_memory_in_megabytes, f"Overuse of memory: total: {total_used_memory}Mb used: {used_memory}Mb, limit: {max_memory_in_megabytes}Mb!!"
            return result

        return wrapper

    return decorator


class AbstractTestParser(ABC):
    """Prefix this class with Abstract so the tests don't run here but only in the children"""

    logger = AirbyteLogger()
    record_types = []

    @classmethod
    def _generate_row(cls, types: List[str]) -> List[Any]:
        """Generates random values with request types"""
        row = []
        for needed_type in types:
            for json_type in cls.record_types:
                if json_type == needed_type:
                    row.append(cls._generate_value(needed_type))
                    break
        return row

    @classmethod
    def _generate_value(cls, typ: str) -> Any:
        if typ not in ["boolean", "integer"] and cls._generate_value("boolean"):
            # return 'None' for +- 33% of all requests
            return None

        if typ == "number":
            while True:
                int_value = cls._generate_value("integer")
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
            return os.urandom(random_length)
        elif typ == "timestamp":
            return datetime.now() + timedelta(seconds=random.randint(0, 7200))
        elif typ == "date":
            dt = cls._generate_value("timestamp")
            return dt.date() if dt else None
        elif typ == "time":
            dt = cls._generate_value("timestamp")
            return dt.time() if dt else None
        raise Exception(f"not supported type: {typ}")

    @classmethod
    @lru_cache
    def cached_cases(cls):
        return cls.cases()

    @classmethod
    @abstractmethod
    def cases(cls) -> List[Mapping[str, Any]]:
        """return a map of test_file dicts in structure:
        {
           "small_file": {"AbstractFileParser": CsvParser(format, master_schema), "filepath": "...", "num_records": 5, "inferred_schema": {...}, line_checks:{}, fails: []},
           "big_file": {"AbstractFileParser": CsvParser(format, master_schema), "filepath": "...", "num_records": 16, "inferred_schema": {...}, line_checks:{}, fails: []}
        ]
        note: line_checks index is 1-based to align with row numbers
        """

    def _get_readmode(self, test_file):
        return "rb" if test_file["AbstractFileParser"].is_binary else "r"

    @memory_limit(1024)
    def test_suite_inferred_schema(self, file_info: Mapping[str, Any]):
        with smart_open(file_info["filepath"], self._get_readmode(file_info)) as f:
            if "test_get_inferred_schema" in file_info["fails"]:
                with pytest.raises(Exception) as e_info:
                    file_info["AbstractFileParser"].get_inferred_schema(f)
                    self.logger.debug(str(e_info))
            else:
                assert file_info["AbstractFileParser"].get_inferred_schema(f) == file_info["inferred_schema"]

    @memory_limit(1024)
    def test_stream_suite_records(self, file_info: Mapping[str, Any]):
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

