"""Simple script to download perf profiling dataset from S3.

Usage:
    cd perf_tests
    poetry install
    poetry run python ./run_perf_tests.py


"""

from __future__ import annotations

import copy
from functools import cache
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

WARMUP_ITERATIONS = 0
MEASURED_ITERATIONS = 3
NUM_FILES = 4
USE_CACHE = False

INCLUDE_BASELINE = True


devnull_destination: ab.Destination | None = None
if not USE_CACHE:
    devnull_destination = ab.get_destination(
    name="destination-e2e-test",
    docker_image="airbyte/destination-e2e-test:latest",
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


def main() -> None:
    config_dict = json.loads(Path(SECRETS_FILE_NAME).read_text())

    if NUM_FILES:
        # Truncate to the specific number of files to test
        config_dict["streams"][0]["globs"] = config_dict["streams"][0]["globs"][:NUM_FILES]

    baseline_config = copy.deepcopy(config_dict)
    baseline_config["streams"][0]["bulk_mode"] = "DISABLED"

    new_config = copy.deepcopy(config_dict)

    new_source = ab.get_source(
        "source-s3",
        pip_url=f"-e {CONNECTOR_DIR.absolute()!s}",
        config=new_config,
        install_root=CONNECTOR_DIR / ".venv-latest-version",
        streams="*",
    )

    for i in range(WARMUP_ITERATIONS + MEASURED_ITERATIONS):
        print(f"======Starting new-version test iteration #{i+1}======")
        if USE_CACHE:
            new_source.read(force_full_refresh=True)
        else:
            devnull_destination.write(
                new_source,
                force_full_refresh=True,
                cache=False,
            )
        print(f"======Finished new-version test iteration #{i+1}======")

    if INCLUDE_BASELINE:
        baseline_source = ab.get_source(
            "source-s3",
            pip_url=f"-e {CONNECTOR_DIR.absolute()!s}",
            install_root=CONNECTOR_DIR / ".venv-latest-version",
            config=baseline_config,
            streams="*",
        )
        for i in range(WARMUP_ITERATIONS + MEASURED_ITERATIONS):
            print(f"======Starting baseline test iteration #{i+1}======")
            if USE_CACHE:
                new_source.read(force_full_refresh=True)
            else:
                devnull_destination.write(
                    baseline_source,
                    force_full_refresh=True,
                    cache=False,
                )
            print(f"======Finished baseline test iteration #{i+1}======")


if __name__ == "__main__":
    main()
