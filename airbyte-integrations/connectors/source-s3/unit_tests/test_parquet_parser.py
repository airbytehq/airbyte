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
from airbyte_cdk import AirbyteLogger
from source_s3.source_files_abstract.formats.parquet_parser import PARQUET_TYPES, ParquetParser

from .abstract_test_parser import AbstractTestParser

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")

logger = AirbyteLogger()
filetype = "parquet"


def tmp_folder():
    return os.path.join(tempfile.mkdtemp())


def _save_parquet_file(filename: str, columns: List[str], rows: List[List[Any]]) -> str:
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


def generate_parquet_file(name: str, columns: Mapping[str, str], num_rows: int, custom_rows: Mapping[int, Mapping[str, Any]] = None) -> str:
    """Generates  a random data and save it to a tmp file"""
    filename = os.path.join(tmp_folder(), name + "." + filetype)
    if os.path.exists(filename):
        return filename

    types = list(columns.values()) if num_rows else []
    rows = [_generate_row(types) for _ in range(num_rows)]
    for n, custom_row in (custom_rows or {}).items():
        rows[n] = custom_row
    return _save_parquet_file(filename, list(columns.keys()) if num_rows else [], rows)


def _generate_row(types: List[str]) -> List[Any]:
    """Generates random values with request types"""
    row = []
    for needed_type in types:
        for json_type in PARQUET_TYPES:
            if json_type == needed_type:
                row.append(_generate_value(needed_type))
                break
    return row


# should just use faker instead of this
def _generate_value(typ: str) -> Any:
    if typ not in ["boolean", "integer"] and _generate_value("boolean"):
        # return 'None' for +- 33% of all requests
        return None

    if typ == "number":
        while True:
            int_value = _generate_value("integer")
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
        dt = _generate_value("timestamp")
        return dt.date() if dt else None
    elif typ == "time":
        dt = _generate_value("timestamp")
        return dt.time() if dt else None
    raise Exception(f"not supported type: {typ}")


def compress(archive_name: str, filename: str) -> str:
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
def prepare_tmp_folder():
    # create tmp folder and remove it after a tests
    os.makedirs(tmp_folder(), exist_ok=True)
    logger.info(f"create the tmp folder: {tmp_folder()}")
    yield
    logger.info(f"remove the tmp folder: {tmp_folder()}")
    shutil.rmtree(tmp_folder(), ignore_errors=True)


def create_test_files() -> List[Mapping[str, Any]]:
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
    params = {"filetype": filetype}
    suite.append(
        {
            "test_alias": "basic 'normal' test",
            "AbstractFileParser": ParquetParser(format=params, master_schema=master_schema),
            "filepath": generate_parquet_file("normal_test", schema, num_records),
            "num_records": num_records,
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }
    )
    # tests custom Parquet parameters (row_groups, batch_size etc)
    params = {
        "filetype": filetype,
        "buffer_size": 1024,
        "columns": ["id", "name", "last_seen"],
        "batch_size": 10,
    }
    num_records = 100
    suite.append(
        {
            "test_alias": "custom parquet parameters",
            "filepath": generate_parquet_file("normal_params_test", schema, num_records),
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
        "filetype": "parquet",
        "batch_size": 10,
    }
    num_records = 100000
    suite.append(
        {
            "test_alias": "big parquet file",
            "filepath": generate_parquet_file("big_parquet_file", schema, num_records),
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
    params = {"filetype": filetype}
    num_records = 20
    test_record = {
        "id": 7,
        "name": _generate_value("string"),
        "valid": False,
        "code": 10,
        "degrees": -9.2,
        "birthday": _generate_value("string"),
        "last_seen": _generate_value("string"),
        "created_at": _generate_value("timestamp"),
        "created_date_at": _generate_value("date"),
        "created_time_at": _generate_value("time"),
    }

    expected_record = copy.deepcopy(test_record)
    expected_record["created_date_at"] = ParquetParser.convert_field_data("date", expected_record["created_date_at"])
    expected_record["created_time_at"] = ParquetParser.convert_field_data("time", expected_record["created_time_at"])
    expected_record["created_at"] = ParquetParser.convert_field_data("timestamp", expected_record["created_at"])

    suite.append(
        {
            "test_alias": "check one record",
            "filepath": generate_parquet_file("check_one_record", schema, num_records, custom_rows={7: list(test_record.values())}),
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
    params = {"filetype": filetype}
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
            "filepath": generate_parquet_file("normal_test", schema, num_records),
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
    params = {"filetype": filetype}
    num_records = 10
    simplified_schema = copy.deepcopy(master_schema)
    simplified_schema.pop("id")
    simplified_schema.pop("name")

    suite.append(
        {
            "test_alias": "tests missing columns in master schema",
            "filepath": generate_parquet_file("normal_test", schema, num_records),
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
            "filepath": generate_parquet_file("empty_file", schema, num_records),
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
                "filepath": compress(
                    archive_type,
                    generate_parquet_file("compression_test", schema, num_records, custom_rows={7: list(test_record.values())}),
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


test_files = create_test_files()


@pytest.mark.parametrize("test_file", argvalues=test_files, ids=[file["test_alias"] for file in test_files])
class TestParquetParser(AbstractTestParser):
    filetype = "parquet"

    @property
    def test_files(self) -> List[Mapping[str, Any]]:
        return []
