#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import bz2
import copy
import gzip
import os
import random
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Mapping

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from source_s3.source_files_abstract.formats.parquet_parser import PARQUET_TYPES, ParquetParser

from .abstract_test_parser import AbstractTestParser

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")


class TestParquetParser(AbstractTestParser):
    filetype = "parquet"

    def _save_parquet_file(self, filename: str, columns: List[str], rows: List[List[Any]]) -> str:
        data = {}
        for col_values in zip(columns, *rows):
            data[col_values[0]] = list(col_values[1:])

        if rows:
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df)
        else:
            table = pa.Table.from_arrays([])

        pq.write_table(table, filename)
        return filename

    def generate_parquet_file(
        self, name: str, columns: Mapping[str, str], num_rows: int, custom_rows: Mapping[int, Mapping[str, Any]] = None
    ) -> str:
        """Generates  a random data and save it to a tmp file"""
        filename = os.path.join(self.tmp_folder, name + "." + self.filetype)
        if os.path.exists(filename):
            return filename

        types = list(columns.values()) if num_rows else []
        rows = [self._generate_row(types) for _ in range(num_rows)]
        for n, custom_row in (custom_rows or {}).items():
            rows[n] = custom_row
        return self._save_parquet_file(filename, list(columns.keys()) if num_rows else [], rows)

    @classmethod
    def _generate_row(cls, types: List[str]) -> List[Any]:
        """Generates random values with request types"""
        row = []
        for needed_type in types:
            for json_type in PARQUET_TYPES:
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

    @property
    def tmp_folder(self):
        return os.path.join(tempfile.gettempdir(), self.__class__.__name__)

    def compress(self, archive_name: str, filename: str) -> str:
        compress_filename = f"{filename}.{archive_name}"
        with open(filename, "rb") as f_in:
            if archive_name == "gz":
                with gzip.open(compress_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            elif archive_name == "bz2":
                with bz2.open(compress_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        return compress_filename

    @pytest.fixture(autouse=True)
    def prepare_tmp_folder(self):
        # create tmp folder and remove it after a tests
        os.makedirs(self.tmp_folder, exist_ok=True)
        self.logger.info(f"create the tmp folder: {self.tmp_folder}")
        yield
        self.logger.info(f"remove the tmp folder: {self.tmp_folder}")
        shutil.rmtree(self.tmp_folder, ignore_errors=True)

    @property
    def test_files(self) -> List[Mapping[str, Any]]:
        schema = {
            "id": "integer",
            "name": "string",
            "valid": "boolean",
            "code": "integer",
            "degrees": "number",
            "birthday": "string",
            "last_seen": "string",
            "created_at": "timestamp",
            "created_date_at": "date",
            "created_time_at": "time",
        }
        # datetime => string type

        master_schema = {k: ParquetParser.parse_field_type(needed_logical_type=v)[0] for k, v in schema.items()}
        suite = []
        # basic 'normal' test
        num_records = 10
        params = {"filetype": self.filetype}
        suite.append(
            {
                "test_alias": "basic 'normal' test",
                "AbstractFileParser": ParquetParser(format=params, master_schema=master_schema),
                "filepath": self.generate_parquet_file("normal_test", schema, num_records),
                "num_records": num_records,
                "inferred_schema": master_schema,
                "line_checks": {},
                "fails": [],
            }
        )
        # tests custom Parquet parameters (row_groups, batch_size etc)
        params = {
            "filetype": self.filetype,
            "buffer_size": 1024,
            "columns": ["id", "name", "last_seen"],
            "batch_size": 10,
        }
        num_records = 100
        suite.append(
            {
                "test_alias": "custom parquet parameters",
                "filepath": self.generate_parquet_file("normal_params_test", schema, num_records),
                "num_records": num_records,
                "AbstractFileParser": ParquetParser(
                    format=params,
                    master_schema=master_schema,
                ),
                "inferred_schema": master_schema,
                "line_checks": {},
                "fails": [],
            }
        )

        # tests a big parquet file (100K records)
        params = {
            "filetype": self.filetype,
            "batch_size": 10,
        }
        num_records = 100000
        suite.append(
            {
                "test_alias": "big parquet file",
                "filepath": self.generate_parquet_file("big_parquet_file", schema, num_records),
                "num_records": num_records,
                "AbstractFileParser": ParquetParser(
                    format=params,
                    master_schema=master_schema,
                ),
                "inferred_schema": master_schema,
                "line_checks": {},
                "fails": [],
            }
        )
        #  check one record
        params = {"filetype": self.filetype}
        num_records = 20
        test_record = {
            "id": 7,
            "name": self._generate_value("string"),
            "valid": False,
            "code": 10,
            "degrees": -9.2,
            "birthday": self._generate_value("string"),
            "last_seen": self._generate_value("string"),
            "created_at": self._generate_value("timestamp"),
            "created_date_at": self._generate_value("date"),
            "created_time_at": self._generate_value("time"),
        }

        expected_record = copy.deepcopy(test_record)
        expected_record["created_date_at"] = ParquetParser.convert_field_data("date", expected_record["created_date_at"])
        expected_record["created_time_at"] = ParquetParser.convert_field_data("time", expected_record["created_time_at"])
        expected_record["created_at"] = ParquetParser.convert_field_data("timestamp", expected_record["created_at"])

        suite.append(
            {
                "test_alias": "check one record",
                "filepath": self.generate_parquet_file(
                    "check_one_record", schema, num_records, custom_rows={7: list(test_record.values())}
                ),
                "num_records": num_records,
                "AbstractFileParser": ParquetParser(
                    format=params,
                    master_schema=master_schema,
                ),
                "inferred_schema": master_schema,
                "line_checks": {8: expected_record},
                "fails": [],
            }
        )

        # extra columns in master schema
        params = {"filetype": self.filetype}
        num_records = 10
        extra_schema = copy.deepcopy(master_schema)
        extra_schema.update(
            {
                "extra_id": "integer",
                "extra_name": "string",
            }
        )
        suite.append(
            {
                "test_alias": "extra columns in master schema",
                "filepath": self.generate_parquet_file("normal_test", schema, num_records),
                "num_records": num_records,
                "AbstractFileParser": ParquetParser(
                    format=params,
                    master_schema=extra_schema,
                ),
                "inferred_schema": master_schema,
                "line_checks": {},
                "fails": [],
            }
        )
        # tests missing columns in master schema
        params = {"filetype": self.filetype}
        num_records = 10
        simplified_schema = copy.deepcopy(master_schema)
        simplified_schema.pop("id")
        simplified_schema.pop("name")

        suite.append(
            {
                "test_alias": "tests missing columns in master schema",
                "filepath": self.generate_parquet_file("normal_test", schema, num_records),
                "num_records": num_records,
                "AbstractFileParser": ParquetParser(
                    format=params,
                    master_schema=simplified_schema,
                ),
                "inferred_schema": master_schema,
                "line_checks": {},
                "fails": [],
            }
        )
        # tests empty file, SHOULD FAIL INFER & STREAM RECORDS
        num_records = 0
        suite.append(
            {
                "test_alias": "empty file",
                "filepath": self.generate_parquet_file("empty_file", schema, num_records),
                "num_records": num_records,
                "AbstractFileParser": ParquetParser(
                    format=params,
                    master_schema={},
                ),
                "inferred_schema": master_schema,
                "line_checks": {},
                "fails": ["test_get_inferred_schema", "test_stream_records"],
            }
        )

        # tests compression: gzip
        num_records = 10
        for archive_type in ["gz", "bz2"]:
            suite.append(
                {
                    "test_alias": f"compression: {archive_type}",
                    "filepath": self.compress(
                        archive_type,
                        self.generate_parquet_file("compression_test", schema, num_records, custom_rows={7: list(test_record.values())}),
                    ),
                    "num_records": num_records,
                    "AbstractFileParser": ParquetParser(
                        format=params,
                        master_schema=master_schema,
                    ),
                    "inferred_schema": master_schema,
                    "line_checks": {8: expected_record},
                    "fails": [],
                }
            )
        return suite
