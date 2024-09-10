"""Simple script to download perf profiling dataset from S3.

Usage:
    pipx install uv
    uv run scripts/download_perf_profile_dataset.py

Inline dependency metadata for `uv`:

# /// script
# requires-python = "==3.10"
# dependencies = [
#     "boto3",
# ]
# ///

"""

from __future__ import annotations

import json
from pathlib import Path

import boto3


S3_BUCKET_NAME = "airbyte-internal-performance"
S3_OBJECTS_PREFIX = "profiling-input-files/json/no_op_source/stream1/"

SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_TARGET_DIR = SCRIPT_DIR / Path(".test-data/perf-profile-dataset")
SECRETS_FILE_NAME = SCRIPT_DIR / Path("../secrets/bulk_jsonl_perf_test_config.json")

AWS_ACCESS_KEY_ID = json.loads(SECRETS_FILE_NAME.read_text())["aws_access_key_id"]
AWS_SECRET_ACCESS_KEY = json.loads(SECRETS_FILE_NAME.read_text())["aws_secret_access_key"]


def main() -> None:
    # Ensure the local target directory exists
    LOCAL_TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # Download perf profiling dataset from S3
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    for object_dict in s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_OBJECTS_PREFIX)["Contents"]:
        object_key = object_dict["Key"]
        print(object_key)
        assert isinstance(object_key, str)
        local_file_name = str(Path(LOCAL_TARGET_DIR) / Path(object_key).name)
        if Path(local_file_name).exists():
            print("File already exists, skipping download.")
            continue

        s3_client.download_file(S3_BUCKET_NAME, object_key, local_file_name + ".partial")
        Path(local_file_name + ".partial").rename(local_file_name)


if __name__ == "__main__":
    main()
