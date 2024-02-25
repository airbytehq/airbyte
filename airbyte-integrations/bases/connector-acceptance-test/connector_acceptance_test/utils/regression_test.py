# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""
This file contains utilities for regression tests.

Regression tests store the output records from one CAT run, for use as expected records in a CAT
run for a new version of the connector.
"""

import json
import sys

import yaml
from connector_acceptance_test.config import Config
from connector_acceptance_test.utils.common import load_config


def update_config_expected_records_path(config: Config, test_output_dir: str, new_config_path: str):
    for test in config.acceptance_tests.basic_read.tests:
        test.expect_records.path = f"{test_output_dir}/{test.expect_records.path}"
    _write_new_config(config, new_config_path)


def _write_new_config(config: Config, new_config_path: str):
    with open(new_config_path, "w") as f:
        yaml.dump(json.loads(config.json()), f)


if __name__ == "__main__":
    original_config_filepath, updated_acceptance_test_config_file_path, test_output_directory = sys.argv[1:]
    orig_config = load_config(original_config_filepath)
    update_config_expected_records_path(orig_config, test_output_directory, updated_acceptance_test_config_file_path)
