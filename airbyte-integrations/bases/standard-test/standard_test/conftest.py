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

import copy
import json
from pathlib import Path
from typing import Optional

import pytest
from airbyte_protocol import AirbyteCatalog, ConfiguredAirbyteCatalog, ConnectorSpecification

from standard_test.connector_runner import ConnectorRunner
from standard_test.utils import load_config


@pytest.fixture(name="base_path")
def base_path_fixture(pytestconfig, standard_test_config):
    """Fixture to define base path for every path-like fixture"""
    if standard_test_config.base_path:
        return Path(standard_test_config.base_path).absolute()
    return Path(pytestconfig.getoption("--standard_test_config")).absolute()


@pytest.fixture(name="standard_test_config")
def standard_test_config_fixture(pytestconfig):
    """Fixture with test's config"""
    return load_config(pytestconfig.getoption("--standard_test_config"))


@pytest.fixture(name="connector_config_path")
def connector_config_path_fixture(inputs, base_path):
    """Fixture with connector's config path (relative to base_path)"""
    return Path(base_path) / getattr(inputs, "config_path")


@pytest.fixture(name="invalid_connector_config_path")
def invalid_connector_config_path_fixture(inputs, base_path):
    """Fixture with connector's config path (relative to base_path)"""
    return Path(base_path) / getattr(inputs, "invalid_config_path")


@pytest.fixture(name="connector_spec_path")
def connector_spec_path_fixture(inputs, base_path):
    """Fixture with connector's specification path (relative to base_path)"""
    return Path(base_path) / getattr(inputs, "spec_path")


@pytest.fixture(name="configured_catalog_path")
def configured_catalog_path_fixture(inputs, base_path):
    """Fixture with connector's configured_catalog path (relative to base_path)"""
    if getattr(inputs, "configured_catalog_path"):
        return Path(base_path) / getattr(inputs, "configured_catalog_path")
    return None


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture(configured_catalog_path) -> Optional[ConfiguredAirbyteCatalog]:
    if configured_catalog_path:
        return ConfiguredAirbyteCatalog.parse_file(configured_catalog_path)
    return None


@pytest.fixture(name="catalog")
def catalog_fixture(configured_catalog: ConfiguredAirbyteCatalog) -> Optional[AirbyteCatalog]:
    if configured_catalog:
        return AirbyteCatalog(streams=[stream.stream for stream in configured_catalog.streams])
    return None


@pytest.fixture(name="image_tag")
def image_tag_fixture(standard_test_config):
    return standard_test_config.connector_image


@pytest.fixture(name="connector_config")
def connector_config_fixture(base_path, connector_config_path):
    with open(str(Path(base_path) / connector_config_path), "r") as file:
        contents = file.read()
    return json.loads(contents)


@pytest.fixture(name="invalid_connector_config")
def invalid_connector_config_fixture(base_path, invalid_connector_config_path):
    """TODO: implement default value - generate from valid config"""
    with open(str(Path(base_path) / invalid_connector_config_path), "r") as file:
        contents = file.read()
    return json.loads(contents)


@pytest.fixture(name="malformed_connector_config")
def malformed_connector_config_fixture(connector_config):
    """TODO: drop required field, add extra"""
    malformed_config = copy.deepcopy(connector_config)
    return malformed_config


@pytest.fixture(name="connector_spec")
def connector_spec_fixture(connector_spec_path) -> ConnectorSpecification:
    return ConnectorSpecification.parse_file(connector_spec_path)


@pytest.fixture(name="docker_runner")
def docker_runner_fixture(image_tag, tmp_path) -> ConnectorRunner:
    return ConnectorRunner(image_tag, volume=tmp_path)


@pytest.fixture(name="validate_output_from_all_streams")
def validate_output_from_all_streams_fixture(inputs):
    """Fixture to provide value of `validate output from all streams` flag"""
    return getattr(inputs, "validate_output_from_all_streams")
