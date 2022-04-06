#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
import os
import random
import shutil
from pathlib import Path
from typing import Any, Mapping, Tuple

import pytest
from smart_open import open as smart_open
from source_files_abstract.formats.csv_parser import CsvParser

from .abstract_test_parser import AbstractTestParser, memory_limit
from .conftest import TMP_FOLDER

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")

CSV_TYPES = {"string": "string", "boolean": "boolean", "number": "number", "integer": "integer"}


class TestCsvParser(AbstractTestParser):
    record_types = CSV_TYPES
    filetype = "csv"

    def cases(self) -> Mapping[str, Any]:
        return {
            "basic_normal_test": {
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_1.csv"),
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
            "custom_csv_parameters": {
                # tests custom CSV parameters (odd delimiter, quote_char, escape_char & newlines in values in the file)
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv", "delimiter": "^", "quote_char": "|", "escape_char": "!", "newlines_in_values": True},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_2_params.csv"),
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
                # tests encoding: Big5
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv", "encoding": "big5"}, master_schema={"id": "integer", "name": "string", "valid": "boolean"}
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_3_enc_Big5.csv"),
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
            "encoding_Arabic_(Windows 1256)": {
                # tests encoding: Arabic (Windows 1256)
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv", "encoding": "windows-1256"},
                    master_schema={"id": "integer", "notes": "string", "valid": "boolean"},
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_4_enc_Arabic.csv"),
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
            "compression_gzip": {
                # tests compression: gzip
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_5.csv.gz"),
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
            "compression_bz2": {
                # tests compression: bz2
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_7_bz2.csv.bz2"),
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
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv"},
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
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_1.csv"),
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
                # TODO: maybe this should fail read_records, but it does pick up all the columns from file despite missing from master schema
                "AbstractFileParser": CsvParser(format={"filetype": "csv"}, master_schema={"id": "integer", "name": "string"}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_1.csv"),
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
            "empty_csv_file": {
                # tests empty file, SHOULD FAIL INFER & STREAM RECORDS
                "AbstractFileParser": CsvParser(format={"filetype": "csv"}, master_schema={}),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_6_empty.csv"),
                "num_records": 0,
                "inferred_schema": {},
                "line_checks": {},
                "fails": ["test_get_inferred_schema", "test_stream_records"],
            },
            "no_header_csv_file": {
                # no header test
                "AbstractFileParser": CsvParser(
                    format={
                        "filetype": "csv",
                        "advanced_options": json.dumps(
                            {"column_names": ["id", "name", "valid", "code", "degrees", "birthday", "last_seen"]}
                        ),
                    },
                    master_schema={},
                ),
                "filepath": os.path.join(SAMPLE_DIRECTORY, "csv/test_file_8_no_header.csv"),
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
        }

    def _process_value(self, value: Any, delimiter: str) -> str:
        if isinstance(value, str):
            return value[:1024].replace(delimiter, "a").replace("'", "").replace('"', "").replace("\\", "")
        elif value is None:
            return ""
        else:
            return str(value)

    def _generate_csv_file(self, filename: str, columns: Mapping[str, str], num_rows: int, delimiter: str) -> str:
        """Generates a random CSV and save it to a tmp file"""
        header_line = delimiter.join(columns.keys())
        types = list(columns.values()) if num_rows else []
        with open(filename, "w") as f:
            f.write(header_line + "\n")
            for _ in range(num_rows):
                row_list = [self._process_value(v, delimiter) for v in self._generate_row(types)]
                f.write(delimiter.join(row_list) + "\n")
        return filename

    def _generate_big_file(
        self, filepath: str, size_in_gigabytes: float, columns_number: int, template_file: str = None
    ) -> Tuple[dict, float]:
        temp_files = [filepath + ".1", filepath + ".2"]
        if template_file:
            shutil.copyfile(template_file, filepath)
            schema = None
        else:
            schema = {f"column {i}": random.choice(["integer", "string", "boolean", "number"]) for i in range(columns_number)}
            self._generate_csv_file(filepath, schema, 456, ",")

        skip_headers = False
        with open(filepath, "r") as f:
            with open(temp_files[0], "w") as tf:
                for line in f:
                    if not skip_headers:
                        skip_headers = True
                        continue
                    tf.write(str(line))

        with open(filepath, "ab") as f:
            while True:
                file_size = os.stat(filepath).st_size / (1024**3)
                if file_size > size_in_gigabytes:
                    break
                with open(temp_files[0], "rb") as tf:  # type: ignore[assignment]
                    with open(temp_files[1], "wb") as tf2:
                        buf = tf.read(50 * 1024**2)  # by 50Mb
                        if buf:
                            f.write(buf)  # type: ignore[arg-type]
                            tf2.write(buf)  # type: ignore[arg-type]
                temp_files.append(temp_files.pop(0))
        # remove temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return schema, file_size

    @memory_limit(20)
    @pytest.mark.order(1)
    def test_big_file(self) -> None:
        """tests a big csv file (>= 1.5G records)"""
        filepath = os.path.join(TMP_FOLDER, "big_csv_file." + self.filetype)
        schema, file_size = self._generate_big_file(filepath, 0.1, 123)
        expected_count = sum(1 for _ in open(filepath)) - 1
        self.logger.info(f"generated file {filepath} with size {file_size}Gb, lines: {expected_count}")
        for _ in range(3):
            parser = CsvParser(
                format={"filetype": self.filetype, "block_size": 5 * 1024**2},
                master_schema=schema,
            )
            expected_file = open(filepath, "r")
            # skip the first header line
            next(expected_file)
            read_count = 0
            with smart_open(filepath, self._get_readmode({"AbstractFileParser": parser})) as f:
                for record in parser.stream_records(f):
                    record_line = ",".join("" if v is None else str(v) for v in record.values())
                    expected_line = next(expected_file).strip("\n")
                    assert record_line == expected_line
                    read_count += 1
            assert read_count == expected_count
            expected_file.close()
