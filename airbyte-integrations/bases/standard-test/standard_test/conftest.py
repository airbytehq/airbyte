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

from airbyte_protocol import ConfiguredAirbyteCatalog, AirbyteCatalog, ConnectorSpecification
from .utils import ConnectorRunner
from .config import Config


def pytest_addoption(parser):
    """ Hook function to add CLI option `standard_test_config`
    """
    parser.addoption(
        "--standard_test_config", action="store", default=".", help="Folder with standard test config - standard_test_config.yml"
    )


def load_config(path: str) -> Config:
    """ Function to load test config, avoid duplication of code in places where we can't use fixture
    """
    path = Path(path) / "standard_test_config.yml"
    if not path.exists():
        pytest.fail(f"config file {path} does not exist")

    with open(str(path), "r") as file:
        data = load(file, Loader=Loader)
        return Config.parse_obj(data)


@pytest.fixture(name="base_path")
def base_path_fixture(pytestconfig, standard_test_config):
    """ Fixture to define base path for every path-like fixture
    """
    if standard_test_config.base_path:
        return Path(standard_test_config.base_path).absolute()
    return Path(pytestconfig.getoption('--standard_test_config')).absolute()


def pytest_generate_tests(metafunc):
    """ Hook function to customize test discovery and parametrization.
        It does two things:
         1. skip test class if its name omitted in the config file (or it has no inputs defined)
         2. parametrize each test with inputs from config file.

        For example config file contains this:
            tests:
              test_suite1:
                - input1: value1
                  input2: value2
                - input1: value3
                  input2: value4
              test_suite2: []

        Hook function will skip test_suite2 and test_suite3, but parametrize test_suite1 with two sets of inputs.
    """
    if "inputs" in metafunc.fixturenames:
        config_key = metafunc.cls.config_key()
        config = load_config(metafunc.config.getoption('--standard_test_config'))
        if not hasattr(config.tests, config_key) or not getattr(config.tests, config_key):
            pytest.skip(f"Skipping {config_key} because not found in the config")
        else:
            test_inputs = getattr(config.tests, config_key)
            if not test_inputs:
                pytest.skip(f"Skipping {config_key} because no inputs provided")

            metafunc.parametrize("inputs", test_inputs)


@pytest.fixture
def standard_test_config(pytestconfig):
    """ Fixture with test's config
    """
    return load_config(pytestconfig.getoption('--standard_test_config'))


@pytest.fixture
def connector_config_path(inputs, base_path):
    """ Fixture with connector's config path (relative to base_path)
    """
    return Path(base_path) / getattr(inputs, "config_path")


@pytest.fixture
def connector_spec_path(inputs, base_path):
    """ Fixture with connector's specification path (relative to base_path)
    """
    return Path(base_path) / getattr(inputs, "spec_path")


@pytest.fixture
def configured_catalog_path(inputs, base_path):
    """ Fixture with connector's configured_catalog path (relative to base_path)
    """
    return Path(base_path) / getattr(inputs, "configured_catalog_path")


@pytest.fixture
def configured_catalog(configured_catalog_path) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog.parse_file(configured_catalog_path)


@pytest.fixture
def catalog(configured_catalog: ConfiguredAirbyteCatalog) -> AirbyteCatalog:
    return AirbyteCatalog(streams=[stream.stream for stream in configured_catalog.streams])


@pytest.fixture
def image_tag(standard_test_config):
    return standard_test_config.connector_image


@pytest.fixture
def connector_config(base_path, connector_config_path):
    with open(str(Path(base_path) / connector_config_path), "r") as file:
        contents = file.read()
    return json.loads(contents)


@pytest.fixture
def connector_spec(connector_spec_path):
    return ConnectorSpecification.parse_file(connector_spec_path)


@pytest.fixture
def docker_runner(image_tag, tmp_path) -> ConnectorRunner:
    return ConnectorRunner(image_tag, volume=tmp_path)
