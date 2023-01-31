#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent.absolute()
pytest_plugins = ("source_acceptance_test.plugin",)


@pytest.fixture(name="create_config", scope="session")
def create_config_fixture():
    secrets_path = HERE.parent / "secrets"
    secrets_path.mkdir(exist_ok=True)
    config_filename = str(secrets_path / "config.json")

    config = {"url": "http://localhost:8080", "access_key": "59662QEPFNCJ3KFL3VCT5VNQ4NHVUF4Y"}

    with open(config_filename, "w+") as fp:
        json.dump(obj=config, fp=fp)


@pytest.fixture(scope="session", autouse=True)
def connector_setup(create_config):
    """This fixture is a placeholder for external resources that acceptance test might require."""
    filename = str(HERE / "docker-compose.yaml")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "docker-compose"], stdout=subprocess.DEVNULL)
    subprocess.check_call(["docker-compose", "-f", filename, "up", "-d"])
    yield
    subprocess.check_call(["docker-compose", "-f", filename, "down", "-v"])
