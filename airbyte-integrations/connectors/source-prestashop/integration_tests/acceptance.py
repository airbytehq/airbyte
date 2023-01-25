#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).parent.absolute()
pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(name="create_config", scope="session")
def create_config_fixture():
    secrets_path = HERE.parent / "secrets"
    secrets_path.mkdir(exist_ok=True)
    config_filename = str(secrets_path / "config.json")

    config = {
        "url": "http://localhost:8080",
        "_allow_http": True,
        "access_key": "59662QEPFNCJ3KFL3VCT5VNQ4NHVUF4Y",
        "start_date": "2021-05-25",
    }

    with open(config_filename, "w+") as fp:
        json.dump(obj=config, fp=fp)


@pytest.fixture(scope="session", autouse=True)
def connector_setup(create_config):
    """This fixture is a placeholder for external resources that acceptance test might require."""
    filename = str(HERE / "docker-compose.yaml")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "docker-compose"], stdout=subprocess.DEVNULL)

    env = None
    AIRBYTE_SAT_CONNECTOR_DIR = os.environ.get("AIRBYTE_SAT_CONNECTOR_DIR")
    if AIRBYTE_SAT_CONNECTOR_DIR:
        env = {**os.environ, "INTEGRATION_TESTS_DIR": os.path.join(AIRBYTE_SAT_CONNECTOR_DIR, "integration_tests")}

    subprocess.check_call(["docker-compose", "-f", filename, "up", "-d"], env=env)
    time.sleep(5)
    yield
    subprocess.check_call(["docker-compose", "-f", filename, "down", "-v"])
