#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
