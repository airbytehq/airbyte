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


import copy
import json
import logging
import os
from logging import Logger
from pathlib import Path
from subprocess import run
from typing import Any, List, MutableMapping, Optional

import pytest
from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConnectorSpecification, Type
from docker import errors
from source_acceptance_test.config import Config
from source_acceptance_test.utils import ConnectorRunner, SecretDict, load_config


@pytest.fixture(name="base_path")
def base_path_fixture(pytestconfig, acceptance_test_config) -> Path:
    """Fixture to define base path for every path-like fixture"""
    if acceptance_test_config.base_path:
        return Path(acceptance_test_config.base_path).absolute()
    return Path(pytestconfig.getoption("--acceptance-test-config")).absolute()


@pytest.fixture(name="acceptance_test_config", scope="session")
def acceptance_test_config_fixture(pytestconfig) -> Config:
    """Fixture with test's config"""
    return load_config(pytestconfig.getoption("--acceptance-test-config", skip=True))


@pytest.fixture(name="connector_config_path")
def connector_config_path_fixture(inputs, base_path) -> Path:
    """Fixture with connector's config path"""
    return Path(base_path) / getattr(inputs, "config_path")


@pytest.fixture(name="invalid_connector_config_path")
def invalid_connector_config_path_fixture(inputs, base_path) -> Path:
    """Fixture with connector's config path"""
    return Path(base_path) / getattr(inputs, "invalid_config_path")


@pytest.fixture(name="connector_spec_path")
def connector_spec_path_fixture(inputs, base_path) -> Path:
    """Fixture with connector's specification path"""
    return Path(base_path) / getattr(inputs, "spec_path")


@pytest.fixture(name="configured_catalog_path")
def configured_catalog_path_fixture(inputs, base_path) -> Optional[str]:
    """Fixture with connector's configured_catalog path"""
    if getattr(inputs, "configured_catalog_path"):
        return Path(base_path) / getattr(inputs, "configured_catalog_path")
    return None


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture(configured_catalog_path, discovered_catalog) -> Optional[ConfiguredAirbyteCatalog]:
    if configured_catalog_path:
        catalog = ConfiguredAirbyteCatalog.parse_file(configured_catalog_path)
        for configured_stream in catalog.streams:
            configured_stream.stream = discovered_catalog.get(configured_stream.stream.name, configured_stream.stream)
        return catalog
    return None


@pytest.fixture(name="image_tag")
def image_tag_fixture(acceptance_test_config) -> str:
    return acceptance_test_config.connector_image


@pytest.fixture(name="connector_config")
def connector_config_fixture(base_path, connector_config_path) -> SecretDict:
    with open(str(connector_config_path), "r") as file:
        contents = file.read()
    return SecretDict(json.loads(contents))


@pytest.fixture(name="invalid_connector_config")
def invalid_connector_config_fixture(base_path, invalid_connector_config_path) -> MutableMapping[str, Any]:
    """TODO: implement default value - generate from valid config"""
    with open(str(invalid_connector_config_path), "r") as file:
        contents = file.read()
    return json.loads(contents)


@pytest.fixture(name="malformed_connector_config")
def malformed_connector_config_fixture(connector_config) -> MutableMapping[str, Any]:
    """TODO: drop required field, add extra"""
    malformed_config = copy.deepcopy(connector_config)
    return malformed_config


@pytest.fixture(name="connector_spec")
def connector_spec_fixture(connector_spec_path) -> ConnectorSpecification:
    return ConnectorSpecification.parse_file(connector_spec_path)


@pytest.fixture(name="docker_runner")
def docker_runner_fixture(image_tag, tmp_path) -> ConnectorRunner:
    return ConnectorRunner(image_tag, volume=tmp_path)


@pytest.fixture(scope="session", autouse=True)
def pull_docker_image(acceptance_test_config) -> None:
    """Startup fixture to pull docker image"""
    image_name = acceptance_test_config.connector_image
    config_filename = "acceptance-test-config.yml"
    try:
        ConnectorRunner(image_name=image_name, volume=Path("."))
    except errors.ImageNotFound:
        pytest.exit(f"Docker image `{image_name}` not found, please check your {config_filename} file", returncode=1)


@pytest.fixture(name="expected_records")
def expected_records_fixture(inputs, base_path) -> List[AirbyteRecordMessage]:
    expect_records = getattr(inputs, "expect_records")
    if not expect_records:
        return []

    with open(str(base_path / getattr(expect_records, "path"))) as f:
        return [AirbyteRecordMessage.parse_raw(line) for line in f]


@pytest.fixture(name="cached_schemas", scope="session")
def cached_schemas_fixture() -> MutableMapping[str, Any]:
    """Simple cache for discovered catalog: stream_name -> json_schema"""
    return {}


@pytest.fixture(name="discovered_catalog")
def discovered_catalog_fixture(connector_config, docker_runner: ConnectorRunner, cached_schemas) -> MutableMapping[str, Any]:
    """JSON schemas for each stream"""
    if not cached_schemas:
        output = docker_runner.call_discover(config=connector_config)
        catalogs = [message.catalog for message in output if message.type == Type.CATALOG]
        for stream in catalogs[-1].streams:
            cached_schemas[stream.name] = stream

    return cached_schemas


@pytest.fixture
def detailed_logger() -> Logger:
    """
    Create logger object for recording detailed test information into a file
    """
    LOG_DIR = "acceptance_tests_logs"
    if os.environ.get("ACCEPTANCE_TEST_DOCKER_CONTAINER"):
        LOG_DIR = os.path.join("/test_input", LOG_DIR)
    run(["mkdir", "-p", LOG_DIR])
    filename = os.environ["PYTEST_CURRENT_TEST"].split("/")[-1].replace(" (setup)", "") + ".txt"
    filename = os.path.join(LOG_DIR, filename)
    formatter = logging.Formatter("%(message)s")
    logger = logging.getLogger(f"detailed_logger {filename}")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename, mode="w")
    fh.setFormatter(formatter)
    logger.log_json_list = lambda l: logger.info(json.dumps(list(l), indent=1))
    logger.handlers = [fh]
    return logger
