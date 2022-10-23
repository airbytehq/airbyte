#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import bz2
import gzip
import linecache
import logging
import os
import random
import sys
import tracemalloc
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Any, Callable, List, Mapping

import pytest
from airbyte_cdk.sources.streams.files import FileInfo


def memory_limit(max_memory_in_megabytes: int, print_limit: int = 20) -> Callable:
    """Runs a test function by a separate process with restricted memory"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: List[Any], **kwargs: Any) -> Any:
            tracemalloc.start()
            result = func(*args, **kwargs)

            # get memory usage immediately after function call, we interested in "first_size" value
            first_size, first_peak = tracemalloc.get_traced_memory()
            # get snapshot immediately just in case we will use it
            snapshot = tracemalloc.take_snapshot()

            # only if we exceeded the quota, build log_messages with traces
            first_size_in_megabytes = first_size / 1024**2
            if first_size_in_megabytes > max_memory_in_megabytes:
                log_messages: List[str] = []
                top_stats = snapshot.statistics("lineno")
                for index, stat in enumerate(top_stats[:print_limit], 1):
                    frame = stat.traceback[0]
                    filename = os.sep.join(frame.filename.split(os.sep)[-2:])
                    log_messages.append("#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024))
                    line = linecache.getline(frame.filename, frame.lineno).strip()
                    if line:
                        log_messages.append(f"    {line}")
                traceback_log = "\n".join(log_messages)
                assert False, f"Overuse of memory, used: {first_size_in_megabytes}Mb, limit: {max_memory_in_megabytes}Mb!!\n{traceback_log}"

            return result

        return wrapper

    return decorator


def create_by_local_file(filepath: str) -> FileInfo:
    "Generates a FileInfo instance for local files"
    if not os.path.exists(filepath):
        return FileInfo(key=filepath, size=0, last_modified=datetime.now())
    return FileInfo(key=filepath, size=os.stat(filepath).st_size, last_modified=datetime.fromtimestamp(os.path.getmtime(filepath)))


class AbstractParserTests(ABC):
    """Prefixed this class with Abstract so the tests don't run here but only in the children"""

    logger = logging.getLogger("airbyte")
    record_types: Mapping[str, Any] = {}

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
    def cached_cases(cls) -> Mapping[str, Any]:
        return cls.cases()

    @classmethod
    @abstractmethod
    def cases(cls) -> Mapping[str, Any]:
        """return a map of test cases in this structure:
        {
           "test_name": {
                "AbstractFileParser": SpecificParserClass(
                    format={format dict as expected by the parser},  # e.g. {"filetype": "csv", "encoding": "big5"}
                    master_schema={dict of actual schema of test file}  # e.g. {"id": "integer", "name": "string"}
                ),
                "filepath": "{point at path to test file}",
                "num_records": {integer value for number of rows to expect from file},
                "inferred_schema": {expected schema from parser inference},  # e.g. {"id": "integer", "name": "string"}
                "line_checks": {check specific lines are parsed correctly},  # e.g. {4: {"id": 4, "name": "bingo"} }
                "fails": []  # empty for pass. Add "test_get_inferred_schema" and/or "test_stream_records" to test fails
            },
           "test_2": etc.
        }
        note: line_checks index is 1-based to align with row numbers
        """

    def _get_readmode(self, file_info: Mapping[str, Any]) -> str:
        return "rb" if file_info["AbstractFileParser"].is_binary else "r"

    @contextmanager
    def _open_and_handle_decompress(self, filepath: str, readmode: str):
        if filepath.endswith(".gz"):
            resource = gzip.open(filepath, readmode)
        elif filepath.endswith(".bz2"):
            resource = bz2.open(filepath, readmode)
        else:
            resource = open(filepath, readmode)
        try:
            yield resource
        finally:
            resource.close()

    @memory_limit(1024)
    def test_suite_inferred_schema(self, file_info: Mapping[str, Any]) -> None:
        with self._open_and_handle_decompress(file_info["filepath"], self._get_readmode(file_info)) as f:
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
        with self._open_and_handle_decompress(filepath, self._get_readmode(file_info)) as f:
            if "test_stream_records" in file_info["fails"]:
                with pytest.raises(Exception) as e_info:
                    [print(r) for r in file_info["AbstractFileParser"].stream_records(f)]
                    self.logger.debug(str(e_info))
            else:
                records = [r for r in file_info["AbstractFileParser"].stream_records(f)]

                assert len(records) == file_info["num_records"]
                for index, expected_record in file_info["line_checks"].items():
                    assert records[index - 1] == expected_record
