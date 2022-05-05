#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
import os
import pprint
import sys
from typing import List


def list_output_files(root_dir: str) -> List[str]:
    return os.listdir(root_dir)


def get_expected_records_for_stream(root_dir: str, filename: str):
    full_path = os.path.join(root_dir, filename)
    with open(full_path, "r") as f:
        records = f.readlines()
        return [json.loads(r) for r in records]


def get_stream_name_from_filename(filename: str):
    return filename.split("_airbyte_raw_")[1].split(".jsonl")[0]


def transform_record_to_expected_record(record, stream):
    print()
    print(record)
    return {"stream": stream, "data": record["_airbyte_data"], "emitted_at": record["_airbyte_emitted_at"]}


if __name__ == "__main__":
    root_dir = "/tmp/airbyte_local/tmp/datatestjson/"
    output_files = list_output_files(root_dir)
    records_to_write = []
    catalog_filename = "sample_files/new_configured_catalog.json"
    with open(catalog_filename, "r") as f:
        catalog = json.loads(f.read())
    # pprint.pprint(catalog)
    streams = catalog["streams"]
    streams_to_expected = set([s["stream"]["name"] for s in streams])
    for stream_file in output_files:
        stream = get_stream_name_from_filename(stream_file)
        if stream in streams_to_expected:
            print(f"stream_file: {stream_file}")
            print(f"stream: {stream}")
            expected_records = get_expected_records_for_stream(root_dir, stream_file)
            pprint.pprint(expected_records)
            for r in expected_records:
                transformed = transform_record_to_expected_record(r, stream)
                records_to_write.append(transformed)
        else:
            print(f"Skipping stream {stream}")
    with open("./integration_tests/generated_expected_records.txt", "w") as f:
        f.writelines([f"{json.dumps(r)}\n" for r in records_to_write])


# --- tests ---
def setup_module():
    global pytest
    global mock


if "pytest" in sys.argv[0]:
    import unittest

    class CreateExpectedRecordsTestcase(unittest.TestCase):
        def test(self):
            assert False
