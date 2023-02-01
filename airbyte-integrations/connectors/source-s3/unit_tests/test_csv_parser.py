#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
import random
import shutil
import string
from pathlib import Path
from typing import Any, List, Mapping, Tuple

import pendulum
import pytest
from smart_open import open as smart_open
from source_s3.source_files_abstract.file_info import FileInfo
from source_s3.source_files_abstract.formats.csv_parser import CsvParser

from .abstract_test_parser import AbstractTestParser, memory_limit
from .conftest import TMP_FOLDER

SAMPLE_DIRECTORY = Path(__file__).resolve().parent.joinpath("sample_files/")

# All possible CSV data types
CSV_TYPES = {
    # logical_type: (json_type, csv_types, convert_function)
    # standard types
    "string": ("string", ["string"], None),
    "boolean": ("boolean", ["boolean"], None),
    "number": ("number", ["number"], None),
    "integer": ("integer", ["integer"], None),
}


def _generate_value(typ: str) -> Any:
    if typ == "string":
        if AbstractTestParser._generate_value("boolean"):
            return None
        random_length = random.randint(0, 512)
        return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random_length))
    return AbstractTestParser._generate_value(typ)


def _generate_row(types: List[str]) -> List[Any]:
    """Generates random values with request types"""
    row = []
    for needed_type in types:
        for json_type in CSV_TYPES:
            if json_type == needed_type:
                value = _generate_value(needed_type)
                if value is None:
                    value = ""
                row.append(str(value))
                break
    return row


def generate_csv_file(filename: str, columns: Mapping[str, str], num_rows: int, delimiter: str) -> str:
    """Generates  a random CSV data and save it to a tmp file"""
    header_line = delimiter.join(columns.keys())
    types = list(columns.values()) if num_rows else []
    with open(filename, "w") as f:
        f.write(header_line + "\n")
        for _ in range(num_rows):
            f.write(delimiter.join(_generate_row(types)) + "\n")
    return filename


def generate_big_file(filepath: str, size_in_gigabytes: float, columns_number: int, template_file: str = None) -> Tuple[dict, float]:
    temp_files = [filepath + ".1", filepath + ".2"]
    if template_file:
        shutil.copyfile(template_file, filepath)
        schema = None
    else:
        schema = {f"column {i}": random.choice(["integer", "string", "boolean", "number"]) for i in range(columns_number)}
        generate_csv_file(filepath, schema, 456, ",")

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


class TestCsvParser(AbstractTestParser):
    record_types = CSV_TYPES
    filetype = "csv"

    @classmethod
    def cases(cls) -> Mapping[str, Any]:
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
            "empty_advanced_options": {
                "AbstractFileParser": CsvParser(
                    format={"filetype": "csv", "advanced_options": ""},
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

    @memory_limit(20)
    @pytest.mark.order(1)
    def test_big_file(self) -> None:
        """tests a big csv file (>= 1.5G records)"""
        filepath = os.path.join(TMP_FOLDER, "big_csv_file." + self.filetype)
        schema, file_size = generate_big_file(filepath, 0.1, 123)
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
                for record in parser.stream_records(f, FileInfo(key=filepath, size=file_size, last_modified=pendulum.now())):
                    record_line = ",".join("" if v is None else str(v) for v in record.values())
                    expected_line = next(expected_file).strip("\n")
                    assert record_line == expected_line
                    read_count += 1
            assert read_count == expected_count
            expected_file.close()
