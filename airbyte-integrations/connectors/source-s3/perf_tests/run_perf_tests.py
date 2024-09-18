"""Simple script to download perf profiling dataset from S3.

Usage:
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

WARMUP_ITERATIONS = 0
MEASURED_ITERATIONS = 2
NUM_FILES = 1


SKIP_BASELINE = False

def main() -> None:
    config_dict = json.loads(Path(SECRETS_FILE_NAME).read_text())

    # Truncate to the specific number of files to test
    config_dict["streams"][0]["globs"] = config_dict["streams"][0]["globs"][:NUM_FILES]

    baseline_config = copy.deepcopy(config_dict)
    baseline_config["streams"][0]["bulk_mode"] = "DISABLED"

    new_config = copy.deepcopy(config_dict)

    if not SKIP_BASELINE:
        old_source = ab.get_source(
            "source-s3",
            pip_url=f"-e {CONNECTOR_DIR.absolute()!s}",
            config=baseline_config,
            install_root=CONNECTOR_DIR / ".venv-latest-version",
            streams="*",
        )

    new_source = ab.get_source(
        "source-s3",
        pip_url=f"-e {CONNECTOR_DIR.absolute()!s}",
        config=new_config,
        install_root=CONNECTOR_DIR / ".venv-latest-version",
        streams="*",
    )

    if not SKIP_BASELINE:
        for i in range(WARMUP_ITERATIONS + MEASURED_ITERATIONS):
            print(f"======Starting prev-version test iteration #{i+1}======")
            old_source.read(force_full_refresh=True)
            print(f"======Finished prev-version test iteration #{i+1}======")

    for i in range(WARMUP_ITERATIONS + MEASURED_ITERATIONS):
        print(f"======Starting new-version test iteration #{i+1}======")
        new_source.read(force_full_refresh=True)
        print(f"======Finished new-version test iteration #{i+1}======")


if __name__ == "__main__":
    main()
