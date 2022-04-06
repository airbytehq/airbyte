#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import copy
import os
from pathlib import Path
from typing import Any, List, Mapping

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from source_files_abstract.formats.parquet_parser import PARQUET_TYPES, ParquetParser

from .abstract_test_parser import AbstractTestParser, compress
from .conftest import TMP_FOLDER

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")


class TestParquetParser(AbstractTestParser):
    filetype = "parquet"
    record_types = PARQUET_TYPES

    def _generate_parquet_file(
        self, name: str, columns: Mapping[str, str], num_rows: int, custom_rows: Mapping[int, List[str]] = None
    ) -> str:
        """Generates  a random data and save it to a tmp file"""
        filename = os.path.join(TMP_FOLDER, name + "." + self.filetype)

        pq_writer = None
        types = list(columns.values()) if num_rows else []
        custom_rows = custom_rows or {}
        column_names = list(columns.keys())
        buffer = []
        for i in range(num_rows):
            buffer.append(custom_rows.get(i) or self._generate_row(types))
            if i != (num_rows - 1) and len(buffer) < 100:
                continue
            data = {col_values[0]: list(col_values[1:]) for col_values in zip(column_names, *buffer)}
            buffer = []
            df = pd.DataFrame(data)
            table = pa.Table.from_pandas(df)
            if not pq_writer:
                pq_writer = pq.ParquetWriter(filename, table.schema)
            pq_writer.write_table(table, row_group_size=100)

        if not pq_writer:
            pq.write_table(pa.Table.from_arrays([]), filename)
        return filename

    def cases(self) -> Mapping[str, Any]:
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
        cases = {}
        # basic 'normal' test
        num_records = 10
        params = {"filetype": self.filetype}
        cases["basic_normal_test"] = {
            "AbstractFileParser": ParquetParser(format=params, master_schema=master_schema),
            "filepath": self._generate_parquet_file("normal_test", schema, num_records),
            "num_records": num_records,
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }
        # tests custom Parquet parameters (row_groups, batch_size etc)
        params = {
            "filetype": self.filetype,
            "buffer_size": 1024,
            "columns": ["id", "name", "last_seen"],
        }
        num_records = 100
        cases["custom_parquet_parameters"] = {
            "filepath": self._generate_parquet_file("normal_params_test", schema, num_records),
            "num_records": num_records,
            "AbstractFileParser": ParquetParser(
                format=params,
                master_schema=master_schema,
            ),
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }

        # tests a big parquet file (100K records)
        params = {
            "filetype": self.filetype,
            "batch_size": 200,
            "use_threads": False,
        }
        num_records = 100000

        cases["big_parquet_file"] = {
            "filepath": self._generate_parquet_file("big_parquet_file", schema, num_records),
            "num_records": num_records,
            "AbstractFileParser": ParquetParser(
                format=params,
                master_schema=master_schema,
            ),
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }

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
        cases["extra_columns_in_master_schema"] = {
            "filepath": self._generate_parquet_file("normal_test", schema, num_records),
            "num_records": num_records,
            "AbstractFileParser": ParquetParser(
                format=params,
                master_schema=extra_schema,
            ),
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }

        # tests missing columns in master schema
        params = {"filetype": self.filetype}
        num_records = 10
        simplified_schema = copy.deepcopy(master_schema)
        simplified_schema.pop("id")
        simplified_schema.pop("name")

        cases["tests_missing_columns_in_master_schema"] = {
            "filepath": self._generate_parquet_file("normal_test", schema, num_records),
            "num_records": num_records,
            "AbstractFileParser": ParquetParser(
                format=params,
                master_schema=simplified_schema,
            ),
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": [],
        }

        # tests empty file, SHOULD FAIL INFER & STREAM RECORDS
        num_records = 0
        cases["empty_file"] = {
            "filepath": self._generate_parquet_file("empty_file", schema, num_records),
            "num_records": num_records,
            "AbstractFileParser": ParquetParser(
                format=params,
                master_schema={},
            ),
            "inferred_schema": master_schema,
            "line_checks": {},
            "fails": ["test_get_inferred_schema", "test_stream_records"],
        }

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

        cases["check_one_record"] = {
            "filepath": self._generate_parquet_file("check_one_record", schema, num_records, custom_rows={7: list(test_record.values())}),
            "num_records": num_records,
            "AbstractFileParser": ParquetParser(
                format=params,
                master_schema=master_schema,
            ),
            "inferred_schema": master_schema,
            "line_checks": {8: expected_record},
            "fails": [],
        }

        # tests compression: gzip
        num_records = 10
        for archive_type in ["gz", "bz2"]:
            cases[f"compression_{archive_type}"] = {
                "filepath": compress(
                    archive_type,
                    self._generate_parquet_file("compression_test", schema, num_records, custom_rows={7: list(test_record.values())}),
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
        return cases
