#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import linecache
import os
import random
import sys
import tracemalloc
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Any, Callable, List, Mapping

import pytest
from airbyte_cdk import AirbyteLogger
from smart_open import open as smart_open
from source_s3.source_files_abstract.file_info import FileInfo


def memory_limit(max_memory_in_megabytes: int, print_limit: int = 20) -> Callable:
    """Runs a test function by a separate process with restricted memory"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            tracemalloc.start()
            result = func(*args, **kwargs)
            snapshot = tracemalloc.take_snapshot()
            snapshot = snapshot.filter_traces(
                (
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                    tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
                    tracemalloc.Filter(False, "<unknown>"),
                )
            )
            log_messages = ["\n"]
            top_stats = snapshot.statistics("lineno")
            for index, stat in enumerate(top_stats[:print_limit], 1):
                frame = stat.traceback[0]
                filename = os.sep.join(frame.filename.split(os.sep)[-2:])
                log_messages.append("#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024))
                line = linecache.getline(frame.filename, frame.lineno).strip()
                if line:
                    log_messages.append(f"    {line}")
            total = sum(stat.size for stat in top_stats) / 1024 ** 2
            log_messages.append("Total allocated size: %.4f Mb" % (total,))
            log_messages = "\n".join(log_messages)
            assert (
                total < max_memory_in_megabytes
            ), f"Overuse of memory, used: {total}Mb, limit: {max_memory_in_megabytes}Mb!!{log_messages}"
            return result

        return wrapper

    return decorator


def create_by_local_file(filepath: str) -> FileInfo:
    "Generates a FileInfo instance for local files"
    if not os.path.exists(filepath):
        return FileInfo(key=filepath, size=0, last_modified=datetime.now())
    return FileInfo(key=filepath, size=os.stat(filepath).st_size, last_modified=datetime.fromtimestamp(os.path.getmtime(filepath)))


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
    @lru_cache(maxsize=None)
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
            file_metadata = create_by_local_file(filepath)
            if "test_stream_records" in file_info["fails"]:
                with pytest.raises(Exception) as e_info:
                    [print(r) for r in file_info["AbstractFileParser"].stream_records(f, file_metadata)]
                    self.logger.debug(str(e_info))
            else:
                records = [r for r in file_info["AbstractFileParser"].stream_records(f, file_metadata)]

                assert len(records) == file_info["num_records"]
                for index, expected_record in file_info["line_checks"].items():
                    assert records[index - 1] == expected_record
