"""Simple script to download perf profiling dataset from S3.

Usage:
    pipx install uv
    uv run scripts/run_perf_tests.py

Inline dependency metadata for `uv`:

# /// script
# requires-python = "==3.10"
# dependencies = [
#     "airbyte",  # PyAirbyte
# ]
# ///

"""

from __future__ import annotations

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


def main() -> None:
    # old_source = ab.get_source(
    #     "source-s3",
    #     pip_url="airbyte-source-s3",
    #     config=json.loads(Path(SECRETS_FILE_NAME).read_text()),
    #     install_root=CONNECTOR_DIR / ".venv-prev-version",
    #     streams="*",
    # )
    Path(CONNECTOR_DIR / ".venv-latest-version").mkdir(parents=True, exist_ok=True)
    new_source = ab.get_source(
        "source-s3",
        pip_url=f"{CONNECTOR_DIR.absolute()!s}",
        config=json.loads(Path(SECRETS_FILE_NAME).read_text()),
        streams="*",
        install_root=CONNECTOR_DIR / ".venv-latest-version",
    )

    # for i in range(3):
    #     logging.info(f"======Starting prev-version test iteration #{i}.======")
    #     old_source.read()
    #     logging.info(f"======Finished prev-version test iteration #{i}.======")

    for i in range(3):
        logging.info(f"======Starting local-version test iteration #{i}.======")
        new_source.read()
        logging.info(f"======Finished local-version test iteration #{i}.======")


if __name__ == "__main__":
    main()
