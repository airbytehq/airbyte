"""Simple script to download perf profiling dataset from S3.

Usage:
    poetry install
    cd perf_tests
    poetry install
    poetry run python ./run_perf_tests.py

"""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path

import airbyte as ab


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.info("Test test test.")

S3_BUCKET_NAME = "airbyte-internal-performance"
S3_OBJECTS_PREFIX = "profiling-input-files/json/no_op_source/stream1/"

SCRIPT_DIR = Path(__file__).resolve().absolute().parent
CONNECTOR_DIR = SCRIPT_DIR.parent
LOCAL_TARGET_DIR = SCRIPT_DIR / Path(".test-data/perf-profile-dataset")
SECRETS_FILE_NAME = SCRIPT_DIR / Path("../secrets/bulk_jsonl_perf_test_config.json")

# This always runs the live (editable) version of the connector from the Poetry venv:
CONNECTOR_EXECUTABLE = SCRIPT_DIR / Path("source-s3-hook.sh")

WARMUP_ITERATIONS = 0
MEASURED_ITERATIONS = 1
NUM_FILES_LIMIT: int | None = None
USE_CACHE = False

INCLUDE_BASELINE = True


devnull_destination: ab.Destination | None = None
if not USE_CACHE:
    devnull_destination = ab.get_destination(
    name="destination-dev-null",
    docker_image="airbyte/destination-dev-null:latest",
    config={
        "test_destination": {
            "test_destination_type": "LOGGING",
            "logging_config": {
                "logging_type": "FirstN",
                "max_entry_count": 100,
            },
        }
    },
)

def get_s3_source(config: dict, local: bool) -> ab.Source:
    if local:
        source = ab.get_source(
            "source-s3",
            config=config,
            local_executable=CONNECTOR_EXECUTABLE,
            streams="*",
        )
    else:
        source = ab.get_source(
            "source-s3",
            config=config,
            version="latest",
            install_root=CONNECTOR_DIR / ".venv-latest-version",
            streams="*",
        )

    return source

def main() -> None:
    config_dict = json.loads(Path(SECRETS_FILE_NAME).read_text())

    if NUM_FILES_LIMIT:
        # Truncate to the specific number of files to test
        config_dict["streams"][0]["globs"] = config_dict["streams"][0]["globs"][:NUM_FILES_LIMIT]

    new_config = copy.deepcopy(config_dict)
    baseline_config = copy.deepcopy(config_dict)

    new_source = get_s3_source(
        config=new_config,
        local=True,
    )

    for i in range(WARMUP_ITERATIONS + MEASURED_ITERATIONS):
        print(f"======Starting new-version test iteration #{i+1}======")
        devnull_destination.write(
            new_source,
            force_full_refresh=True,
            cache=False,
        )
        print(f"======Finished new-version test iteration #{i+1}======")

    if INCLUDE_BASELINE:
        baseline_source = get_s3_source(
            config=baseline_config,
            local=False,
        )
        for i in range(WARMUP_ITERATIONS + MEASURED_ITERATIONS):
            print(f"======Starting baseline test iteration #{i+1}======")
            devnull_destination.write(
                baseline_source,
                force_full_refresh=True,
                cache=False,
            )
            print(f"======Finished baseline test iteration #{i+1}======")


if __name__ == "__main__":
    main()
