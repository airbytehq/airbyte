#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import copy
import json
import logging
import os
from glob import glob
from logging import Logger
from pathlib import Path
from subprocess import STDOUT, check_output, run
from typing import Any, List, MutableMapping, Optional, Set

import pytest
from airbyte_cdk.models import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConnectorSpecification, Type
from docker import errors
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import Config, EmptyStreamConfiguration, ExpectedRecordsConfig
from source_acceptance_test.tests import TestBasicRead
from source_acceptance_test.utils import (
    ConnectorRunner,
    SecretDict,
    build_configured_catalog_from_custom_catalog,
    build_configured_catalog_from_discovered_catalog_and_empty_streams,
    filter_output,
    load_config,
    load_yaml_or_json_path,
)


@pytest.fixture(name="acceptance_test_config", scope="session")
def acceptance_test_config_fixture(pytestconfig) -> Config:
    """Fixture with test's config"""
    return load_config(pytestconfig.getoption("--acceptance-test-config", skip=True))


@pytest.fixture(name="base_path")
def base_path_fixture(pytestconfig, acceptance_test_config) -> Path:
    """Fixture to define base path for every path-like fixture"""
    if acceptance_test_config.base_path:
        return Path(acceptance_test_config.base_path).absolute()
    return Path(pytestconfig.getoption("--acceptance-test-config")).absolute()


@pytest.fixture(name="test_strictness_level", scope="session")
def test_strictness_level_fixture(acceptance_test_config: Config) -> Config.TestStrictnessLevel:
    return acceptance_test_config.test_strictness_level


@pytest.fixture(name="cache_discovered_catalog", scope="session")
def cache_discovered_catalog_fixture(acceptance_test_config: Config) -> bool:
    return acceptance_test_config.cache_discovered_catalog


@pytest.fixture(name="connector_config_path")
def connector_config_path_fixture(inputs, base_path) -> Path:
    """Fixture with connector's config path. The path to the latest updated configurations will be returned if any."""
    original_configuration_path = Path(base_path) / getattr(inputs, "config_path")
    updated_configurations_glob = f"{original_configuration_path.parent}/updated_configurations/{original_configuration_path.stem}|**{original_configuration_path.suffix}"
    existing_configurations_path_creation_time = [
        (config_file_path, os.path.getctime(config_file_path)) for config_file_path in glob(updated_configurations_glob)
    ]
    if existing_configurations_path_creation_time:
        existing_configurations_path_creation_time.sort(key=lambda x: x[1])
        most_recent_configuration_path = existing_configurations_path_creation_time[-1][0]
    else:
        most_recent_configuration_path = original_configuration_path
    logging.info(f"Using {most_recent_configuration_path} as configuration. It is the most recent version.")
    return Path(most_recent_configuration_path)


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
def configured_catalog_fixture(
    configured_catalog_path: Optional[str],
    discovered_catalog: MutableMapping[str, AirbyteStream],
) -> ConfiguredAirbyteCatalog:
    """Build a configured catalog.
    If a configured catalog path is given we build a configured catalog from it, we build it from the discovered catalog otherwise.
    """
    if configured_catalog_path:
        return build_configured_catalog_from_custom_catalog(configured_catalog_path, discovered_catalog)
    else:
        return build_configured_catalog_from_discovered_catalog_and_empty_streams(discovered_catalog, set())


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
def docker_runner_fixture(image_tag, tmp_path, connector_config_path) -> ConnectorRunner:
    return ConnectorRunner(image_tag, volume=tmp_path, connector_configuration_path=connector_config_path)


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


@pytest.fixture(name="empty_streams")
def empty_streams_fixture(inputs, test_strictness_level) -> Set[EmptyStreamConfiguration]:
    empty_streams = getattr(inputs, "empty_streams", set())
    if test_strictness_level is Config.TestStrictnessLevel.high and empty_streams:
        all_empty_streams_have_bypass_reasons = all([bool(empty_stream.bypass_reason) for empty_stream in inputs.empty_streams])
        if not all_empty_streams_have_bypass_reasons:
            pytest.fail("A bypass_reason must be filled in for all empty streams when test_strictness_level is set to high.")
    return empty_streams


@pytest.fixture(name="expect_records_config")
def expect_records_config_fixture(inputs):
    return inputs.expect_records


@pytest.fixture(name="expected_records_by_stream")
def expected_records_by_stream_fixture(
    test_strictness_level: Config.TestStrictnessLevel,
    configured_catalog: ConfiguredAirbyteCatalog,
    empty_streams: Set[EmptyStreamConfiguration],
    expect_records_config: ExpectedRecordsConfig,
    base_path,
) -> MutableMapping[str, List[MutableMapping]]:
    def enforce_high_strictness_level_rules(expect_records_config, configured_catalog, empty_streams, records_by_stream) -> Optional[str]:
        error_prefix = "High strictness level error: "
        if expect_records_config is None:
            pytest.fail(error_prefix + "expect_records must be configured for the basic_read test.")
        elif expect_records_config.path:
            not_seeded_streams = find_not_seeded_streams(configured_catalog, empty_streams, records_by_stream)
            if not_seeded_streams:
                pytest.fail(
                    error_prefix
                    + f"{', '.join(not_seeded_streams)} streams are declared in the catalog but do not have expected records. Please add expected records to {expect_records_config.path} or declare these streams in empty_streams."
                )
        else:
            if not getattr(expect_records_config, "bypass_reason", None):
                pytest.fail(error_prefix / "A bypass reason must be filled if no path to expected records is provided.")

    expected_records_by_stream = {}
    if expect_records_config:
        if expect_records_config.path:
            expected_records_file_path = str(base_path / expect_records_config.path)
            with open(expected_records_file_path, "r") as f:
                all_records = [AirbyteRecordMessage.parse_raw(line) for line in f]
                expected_records_by_stream = TestBasicRead.group_by_stream(all_records)

    if test_strictness_level is Config.TestStrictnessLevel.high:
        enforce_high_strictness_level_rules(expect_records_config, configured_catalog, empty_streams, expected_records_by_stream)
    return expected_records_by_stream


def find_not_seeded_streams(
    configured_catalog: ConfiguredAirbyteCatalog,
    empty_streams: Set[EmptyStreamConfiguration],
    records_by_stream: MutableMapping[str, List[MutableMapping]],
) -> Set[str]:
    stream_names_in_catalog = set([configured_stream.stream.name for configured_stream in configured_catalog.streams])
    empty_streams_names = set([stream.name for stream in empty_streams])
    expected_record_stream_names = set(records_by_stream.keys())
    expected_seeded_stream_names = stream_names_in_catalog - empty_streams_names

    return expected_seeded_stream_names - expected_record_stream_names


@pytest.fixture(name="cached_schemas", scope="session")
def cached_schemas_fixture() -> MutableMapping[str, AirbyteStream]:
    """Simple cache for discovered catalog: stream_name -> json_schema"""
    return {}


@pytest.fixture(name="previous_cached_schemas", scope="session")
def previous_cached_schemas_fixture() -> MutableMapping[str, AirbyteStream]:
    """Simple cache for discovered catalog of previous connector: stream_name -> json_schema"""
    return {}


@pytest.fixture(name="discovered_catalog")
def discovered_catalog_fixture(
    connector_config, docker_runner: ConnectorRunner, cached_schemas, cache_discovered_catalog: bool
) -> MutableMapping[str, AirbyteStream]:
    """JSON schemas for each stream"""
    if not cached_schemas or not cache_discovered_catalog:
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
    if previous_connector_docker_runner is None:
        logging.warning(
            "\n We could not retrieve the previous discovered catalog as a connector runner for the previous connector version could not be instantiated."
        )
        return None
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
