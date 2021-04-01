"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from pathlib import Path

import pytest
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from airbyte_protocol import ConfiguredAirbyteCatalog, AirbyteCatalog
from .utils import ConnectorRunner
from .config import Config


def pytest_addoption(parser):
    parser.addoption(
        "--standard_test_config", action="store", default=".", help="Folder with standard test config - standard_test_config.yml"
    )


HERE = Path(__file__).parent.absolute()


@pytest.fixture
def check_config(request, config):
    if request.node.name not in config["tests"]:
        pytest.skip("Skipping because not found in config")
    request.inputs = config["tests"][request.node.name]["inputs"]


@pytest.fixture
def standard_test_config():
    path = Path(pytest.config.getoption('--standard_test_config')) / "standard_test_config.yml"
    with open(str(path), "r") as file:
        data = load(file, Loader=Loader)
        return Config.parse_obj(**data)


@pytest.fixture
def config_path():
    return HERE.parent / "secrets" / "config.json"


@pytest.fixture
def spec_path():
    return HERE.parent / "source_hubspot" / "spec.json"


@pytest.fixture
def configured_catalog_path():
    return HERE.parent / "sample_files" / "configured_catalog.json"


@pytest.fixture
def configured_catalog(configured_catalog_path) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog.parse_file(configured_catalog_path)


@pytest.fixture
def catalog(configured_catalog: ConfiguredAirbyteCatalog) -> AirbyteCatalog:
    return AirbyteCatalog(streams=[stream.stream for stream in configured_catalog.streams])


@pytest.fixture
def image_tag(standard_test_config):
    return standard_test_config.connector_image
    # return "airbyte/source-hubspot:dev"


@pytest.fixture
def config(config_path):
    with open(config_path, "r") as file:
        contents = file.read()
    return json.loads(contents)


@pytest.fixture
def docker_runner(image_tag, tmp_path) -> ConnectorRunner:
    return ConnectorRunner("airbyte/source-hubspot:dev", volume=tmp_path)
