#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import os
import random
import string
import tempfile
from typing import Iterator

SAMPLE_DIR = os.path.join(tempfile.gettempdir(), "sample_files")
SCHEMA_CORE = {"name": str}
SCHEMA_1 = {**SCHEMA_CORE, **{"valid": bool}}
SCHEMA_DIFF_1 = {**SCHEMA_CORE, **{"location": str}}
SCHEMA_DIFF_2 = {**SCHEMA_1, **{"percentage": float, "nullable": None}}
SCHEMA_INCOMPATIBLE = dict(SCHEMA_1, valid=str)
STRING_LENGTH = 10


def _generate_string(length: int):
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


def _generate_bool():
    return random.choice([True, False])


def _generate_float():
    sign = random.choice([-1, 1])
    magnitude = random.randint(1, 100)
    return round(sign * magnitude * random.random(), 2)


def _data_generator(start_id: int, num_rows: int, schema: dict) -> Iterator:
    yield ["id"] + list(schema.keys())
    for x in range(num_rows):
        row = [start_id + x]
        for typ in schema.values():
            if typ is str:
                row.append(_generate_string(STRING_LENGTH))
            elif typ is bool:
                row.append(_generate_bool())
            elif typ is float:
                row.append(_generate_float())
            else:
                row.append(None)
        yield (row)


def _create_file(dirpath, filename):
    if not os.path.exists(dirpath):
        print(f"creating dir(s): {dirpath}")
        os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename)
    print(f"creating file: {filepath}")
    open(filepath, "w+").close()
    return filepath


def _format_row_for_csv(row: list):
    return ",".join([str(x) for x in row]) + "\n"


def _append_csv_row_to_file(csv_row: str, filepath: str):
    with open(filepath, "a") as f:
        f.write(csv_row)


def _build_data_file(name: str, start_id: int, num_rows: int, schema: dict, custom_dir: str = None):
    dir = custom_dir if custom_dir is not None else SAMPLE_DIR
    fpath = _create_file(dir, name)
    for row in _data_generator(start_id, num_rows, schema):
        _append_csv_row_to_file(_format_row_for_csv(row), fpath)


def generate_sample_files():
    _build_data_file("simple_test.csv", start_id=1, num_rows=8, schema=SCHEMA_1)
    _build_data_file("simple_test_2.csv", start_id=9, num_rows=3, schema=SCHEMA_1)
    _build_data_file("simple_test_3.csv", start_id=12, num_rows=6, schema=SCHEMA_1)
    _build_data_file("no_rows.csv", start_id=1, num_rows=0, schema=SCHEMA_1)
    _build_data_file("multi_file_diffschema_1.csv", start_id=9, num_rows=3, schema=SCHEMA_DIFF_1)
    _build_data_file("multi_file_diffschema_2.csv", start_id=12, num_rows=6, schema=SCHEMA_DIFF_2)
    _build_data_file("incompatible_schema.csv", start_id=1, num_rows=8, schema=SCHEMA_INCOMPATIBLE)
    _build_data_file("file_to_skip.csv", start_id=1, num_rows=2, schema=SCHEMA_1)
    _build_data_file("file_to_skip.txt", start_id=1, num_rows=2, schema=SCHEMA_1)
    _build_data_file(
        "simple_test.csv", start_id=1, num_rows=8, schema=SCHEMA_1, custom_dir=os.path.join(SAMPLE_DIR, "pattern_match_test/this_folder")
    )
    _build_data_file(
        "file_to_skip.csv",
        start_id=1,
        num_rows=2,
        schema=SCHEMA_1,
        custom_dir=os.path.join(SAMPLE_DIR, "pattern_match_test/not_this_folder"),
    )
    _build_data_file(
        "file_to_skip.txt",
        start_id=1,
        num_rows=2,
        schema=SCHEMA_1,
        custom_dir=os.path.join(SAMPLE_DIR, "pattern_match_test/not_this_folder"),
    )
