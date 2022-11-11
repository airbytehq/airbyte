#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import copy
import json
import logging
import os
from logging import Logger
from pathlib import Path
from subprocess import STDOUT, check_output, run
from typing import Any, List, MutableMapping, Optional

import pytest
from airbyte_cdk.models import (
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    Type,
)
from docker import errors
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import Config
from source_acceptance_test.utils import ConnectorRunner, SecretDict, filter_output, load_config, load_yaml_or_json_path


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
def configured_catalog_fixture(configured_catalog_path, discovered_catalog) -> ConfiguredAirbyteCatalog:
    """Take ConfiguredAirbyteCatalog from discover command by default"""
    if configured_catalog_path:
        catalog = ConfiguredAirbyteCatalog.parse_file(configured_catalog_path)
        for configured_stream in catalog.streams:
            configured_stream.stream = discovered_catalog.get(configured_stream.stream.name, configured_stream.stream)
        return catalog
    streams = [
        ConfiguredAirbyteStream(
            stream=stream,
            sync_mode=stream.supported_sync_modes[0],
            destination_sync_mode=DestinationSyncMode.append,
            cursor_field=stream.default_cursor_field,
            primary_key=stream.source_defined_primary_key,
        )
        for _, stream in discovered_catalog.items()
    ]
    return ConfiguredAirbyteCatalog(streams=streams)


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
    spec_obj = load_yaml_or_json_path(connector_spec_path)
    return ConnectorSpecification.parse_obj(spec_obj)


@pytest.fixture(name="docker_runner")
def docker_runner_fixture(image_tag, tmp_path) -> ConnectorRunner:
    return ConnectorRunner(image_tag, volume=tmp_path)


@pytest.fixture(name="previous_connector_image_name")
def previous_connector_image_name_fixture(image_tag, inputs) -> str:
    """Fixture with previous connector image name to use for backward compatibility tests"""
    return f"{image_tag.split(':')[0]}:{inputs.backward_compatibility_tests_config.previous_connector_version}"


@pytest.fixture(name="previous_connector_docker_runner")
def previous_connector_docker_runner_fixture(previous_connector_image_name, tmp_path) -> ConnectorRunner:
    """Fixture to create a connector runner with the previous connector docker image.
    Returns None if the latest image was not found, to skip downstream tests if the current connector is not yet published to the docker registry.
    Raise not found error if the previous connector image is not latest and expected to be published.
    """
    try:
        return ConnectorRunner(previous_connector_image_name, volume=tmp_path / "previous_connector")
    except (errors.NotFound, errors.ImageNotFound) as e:
        if previous_connector_image_name.endswith("latest"):
            logging.warning(
                f"\n We did not find the {previous_connector_image_name} image for this connector. This probably means this version has not yet been published to an accessible docker registry like DockerHub."
            )
            return None
        else:
            raise e


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
def cached_schemas_fixture() -> MutableMapping[str, AirbyteStream]:
    """Simple cache for discovered catalog: stream_name -> json_schema"""
    return {}


@pytest.fixture(name="previous_cached_schemas", scope="session")
def previous_cached_schemas_fixture() -> MutableMapping[str, AirbyteStream]:
    """Simple cache for discovered catalog of previous connector: stream_name -> json_schema"""
    return {}


@pytest.fixture(name="discovered_catalog")
def discovered_catalog_fixture(connector_config, docker_runner: ConnectorRunner, cached_schemas) -> MutableMapping[str, AirbyteStream]:
    """JSON schemas for each stream"""
    if not cached_schemas:
        output = docker_runner.call_discover(config=connector_config)
        catalogs = [message.catalog for message in output if message.type == Type.CATALOG]
        for stream in catalogs[-1].streams:
            cached_schemas[stream.name] = stream

    return cached_schemas


@pytest.fixture(name="previous_discovered_catalog")
def previous_discovered_catalog_fixture(
    connector_config, previous_connector_docker_runner: ConnectorRunner, previous_cached_schemas
) -> MutableMapping[str, AirbyteStream]:
    """JSON schemas for each stream"""
    if not previous_cached_schemas:
        output = previous_connector_docker_runner.call_discover(config=connector_config)
        catalogs = [message.catalog for message in output if message.type == Type.CATALOG]
        for stream in catalogs[-1].streams:
            previous_cached_schemas[stream.name] = stream
    return previous_cached_schemas


@pytest.fixture
def detailed_logger() -> Logger:
    """
    Create logger object for recording detailed test information into a file
    """
    LOG_DIR = "acceptance_tests_logs"
    if os.environ.get("ACCEPTANCE_TEST_DOCKER_CONTAINER"):
        LOG_DIR = os.path.join("/test_input", LOG_DIR)
    run(["mkdir", "-p", LOG_DIR])
    filename = os.environ["PYTEST_CURRENT_TEST"].split("/")[-1].replace(" (setup)", "").replace(":", "_") + ".txt"
    filename = os.path.join(LOG_DIR, filename)
    formatter = logging.Formatter("%(message)s")
    logger = logging.getLogger(f"detailed_logger {filename}")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename, mode="w")
    fh.setFormatter(formatter)
    logger.log_json_list = lambda l: logger.info(json.dumps(list(l), indent=1))
    logger.handlers = [fh]
    return logger


@pytest.fixture(name="actual_connector_spec")
def actual_connector_spec_fixture(request: BaseTest, docker_runner: ConnectorRunner) -> ConnectorSpecification:
    if not request.instance.spec_cache:
        output = docker_runner.call_spec()
        spec_messages = filter_output(output, Type.SPEC)
        assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
        spec = spec_messages[0].spec
        request.instance.spec_cache = spec
    return request.instance.spec_cache


@pytest.fixture(name="previous_connector_spec")
def previous_connector_spec_fixture(
    request: BaseTest, previous_connector_docker_runner: ConnectorRunner
) -> Optional[ConnectorSpecification]:
    if previous_connector_docker_runner is None:
        logging.warning(
            "\n We could not retrieve the previous connector spec as a connector runner for the previous connector version could not be instantiated."
        )
        return None
    if not request.instance.previous_spec_cache:
        output = previous_connector_docker_runner.call_spec()
        spec_messages = filter_output(output, Type.SPEC)
        assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
        spec = spec_messages[0].spec
        request.instance.previous_spec_cache = spec
    return request.instance.previous_spec_cache


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished, right before returning the exit status to the system.
    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionfinish
    """
    logger = logging.getLogger()

    # this is specifically for contributors to run tests locally and show success for a git hash
    # therefore if this fails for any reason we just treat as a no-op
    try:
        result = "PASSED" if session.testscollected > 0 and session.testsfailed == 0 else "FAILED"
        print()  # create a line break
        logger.info(
            # session.startdir gives local path to the connector folder, so we can verify which cnctr was tested
            f"{session.startdir} - SAT run - "
            # using subprocess.check_output to run cmd to get git hash
            f"{check_output('git rev-parse HEAD', stderr=STDOUT, shell=True).decode('ascii').strip()}"
            f" - {result}"
        )
    except Exception as e:
        logger.info(e)  # debug
        pass
