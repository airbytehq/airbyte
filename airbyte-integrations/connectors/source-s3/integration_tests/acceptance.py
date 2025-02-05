#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
from pathlib import Path
from typing import Iterable

import pytest
import yaml


pytest_plugins = ("connector_acceptance_test.plugin",)
logger = logging.getLogger("airbyte")


@pytest.fixture(scope="session", autouse=True)
def connector_setup() -> Iterable[None]:
    """This fixture is responsible for configuring AWS credentials that are used for assuming role during the IAM role based authentication."""
    config_file_path = "secrets/config_iam_role.json"
    acceptance_test_config_file_path = "acceptance-test-config.yml"

    # Read environment variables from the JSON file
    with open(config_file_path, "r") as file:
        config = json.load(file)

    # Prepare environment variables to append to the YAML file
    env_vars = {
        "custom_environment_variables": {
            "AWS_ASSUME_ROLE_EXTERNAL_ID": config["acceptance_test_aws_external_id"],
            "AWS_ACCESS_KEY_ID": config["acceptance_test_aws_access_key_id"],
            "AWS_SECRET_ACCESS_KEY": config["acceptance_test_aws_secret_access_key"],
        }
    }

    # Append environment variables to the YAML file
    yaml_path = Path(acceptance_test_config_file_path)
    if yaml_path.is_file():
        with open(acceptance_test_config_file_path, "r") as file:
            existing_data = yaml.safe_load(file) or {}
        existing_data.update(env_vars)
        with open(acceptance_test_config_file_path, "w") as file:
            yaml.safe_dump(existing_data, file)
    else:
        raise Exception(f"{acceptance_test_config_file_path} does not exist.")

    yield
