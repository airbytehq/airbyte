#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import copy
import itertools
import json
import logging
import os
import sys
from glob import glob
from logging import Logger
from pathlib import Path
from subprocess import STDOUT, check_output, run
from typing import Any, List, Mapping, MutableMapping, Optional, Set

import dagger
import pytest
from airbyte_protocol.models import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConnectorSpecification, Type
from connector_acceptance_test.base import BaseTest
from connector_acceptance_test.config import (
    ClientContainerConfig,
    Config,
    EmptyStreamConfiguration,
    ExpectedRecordsConfig,
    IgnoredFieldsConfiguration,
)
from connector_acceptance_test.tests import TestBasicRead
from connector_acceptance_test.utils import (
    SecretDict,
    build_configured_catalog_from_custom_catalog,
    build_configured_catalog_from_discovered_catalog_and_empty_streams,
    client_container_runner,
    connector_runner,
    filter_output,
    is_manifest_file,
    load_config,
    load_yaml_or_json_path,
    parse_manifest_spec,
)


@pytest.fixture(name="acceptance_test_config", scope="session")
def acceptance_test_config_fixture(pytestconfig) -> Config:
    """Fixture with test's config"""
    return load_config(pytestconfig.getoption("--acceptance-test-config", skip=True))


@pytest.fixture(name="base_path", scope="session")
def base_path_fixture(pytestconfig, acceptance_test_config) -> Path:
    """Fixture to define base path for every path-like fixture"""
    if acceptance_test_config.base_path:
        return Path(acceptance_test_config.base_path).absolute()
    return Path(pytestconfig.getoption("--acceptance-test-config")).absolute()


@pytest.fixture(name="test_strictness_level", scope="session")
def test_strictness_level_fixture(acceptance_test_config: Config) -> Config.TestStrictnessLevel:
    return acceptance_test_config.test_strictness_level


@pytest.fixture(name="custom_environment_variables", scope="session")
def custom_environment_variables_fixture(acceptance_test_config: Config) -> Mapping:
    return acceptance_test_config.custom_environment_variables


@pytest.fixture(name="deployment_mode")
def deployment_mode_fixture(inputs) -> Optional[str]:
    return getattr(inputs, "deployment_mode", None)


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


@pytest.fixture(name="image_tag", scope="session")
def image_tag_fixture(acceptance_test_config) -> str:
    return acceptance_test_config.connector_image


@pytest.fixture(name="connector_config")
def connector_config_fixture(base_path, connector_config_path) -> Optional[SecretDict]:
    try:
        with open(str(connector_config_path), "r") as file:
            contents = file.read()

        return SecretDict(json.loads(contents))
    except FileNotFoundError:
        logging.warning(f"Connector config file not found at {connector_config_path}")
        return None


@pytest.fixture(name="client_container_config")
def client_container_config_fixture(inputs, base_path, acceptance_test_config) -> Optional[ClientContainerConfig]:
    """Fixture with connector's setup/teardown Dockerfile path, if it exists."""
    if hasattr(inputs, "client_container_config") and inputs.client_container_config:
        return inputs.client_container_config


@pytest.fixture(name="client_container_config_global", scope="session")
async def client_container_config_global_fixture(acceptance_test_config: Config) -> ClientContainerConfig:
    if (
        hasattr(acceptance_test_config.acceptance_tests, "client_container_config")
        and acceptance_test_config.acceptance_tests.client_container_config
    ):
        return acceptance_test_config.acceptance_tests.client_container_config


@pytest.fixture(name="client_container_config_secrets")
def client_container_config_secrets_fixture(base_path, client_container_config) -> Optional[SecretDict]:
    if client_container_config and hasattr(client_container_config, "secrets_path") and client_container_config.secrets_path:
        with open(str(base_path / client_container_config.secrets_path), "r") as file:
            contents = file.read()
        return SecretDict(json.loads(contents))
    return None


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
def connector_spec_fixture(connector_spec_path) -> Optional[ConnectorSpecification]:
    try:
        spec_obj = load_yaml_or_json_path(connector_spec_path)
        # handle the case where a manifest.yaml is specified as the spec file
        if is_manifest_file(connector_spec_path):
            return parse_manifest_spec(spec_obj)
        return ConnectorSpecification.parse_obj(spec_obj)
    except FileNotFoundError:
        return None


@pytest.fixture(scope="session")
def anyio_backend():
    """Determine the anyio backend to use for the tests.
    anyio allows us to run async tests.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def dagger_client(anyio_backend):
    """Exposes a Dagger client available for the whole test session.
    Dagger is a tool to programmatically create and interact with containers with out of the box caching.
    More info here: https://dagger.io/
    """
    async with dagger.Connection(config=dagger.Config(log_output=sys.stderr)) as client:
        yield client


@pytest.fixture(scope="session")
async def connector_container(dagger_client, image_tag):
    connector_container = await connector_runner.get_connector_container(dagger_client, image_tag)
    if cachebuster := os.environ.get("CACHEBUSTER"):
        connector_container = connector_container.with_env_variable("CACHEBUSTER", cachebuster)
    return await connector_container


@pytest.fixture(name="docker_runner", autouse=True)
def docker_runner_fixture(
    connector_container, connector_config_path, custom_environment_variables, deployment_mode
) -> connector_runner.ConnectorRunner:
    return connector_runner.ConnectorRunner(
        connector_container,
        connector_configuration_path=connector_config_path,
        custom_environment_variables=custom_environment_variables,
        deployment_mode=deployment_mode,
    )


@pytest.fixture(autouse=True)
async def client_container(
    base_path: Path,
    dagger_client: dagger.Client,
    client_container_config: Optional[ClientContainerConfig],
) -> Optional[dagger.Container]:
    if client_container_config:
        return await client_container_runner.get_client_container(
            dagger_client,
            base_path,
            base_path / client_container_config.client_container_dockerfile_path,
        )


@pytest.fixture(scope="session")
async def client_final_teardown_container(
    base_path: Path,
    dagger_client: dagger.Client,
    client_container_config_global: Optional[ClientContainerConfig],
) -> Optional[dagger.Container]:
    if client_container_config_global:
        return await client_container_runner.get_client_container(
            dagger_client,
            base_path,
            base_path / client_container_config_global.client_container_dockerfile_path,
        )


@pytest.fixture(autouse=True)
async def setup_and_teardown(
    client_container: Optional[dagger.Container],
    client_container_config: Optional[ClientContainerConfig],
    client_container_config_secrets: Optional[SecretDict],
    base_path: Path,
):
    if client_container and hasattr(client_container_config, "setup_command") and client_container_config.setup_command:
        logging.info("Running setup")
        setup_teardown_container = await client_container_runner.do_setup(
            client_container,
            client_container_config.setup_command,
            client_container_config_secrets,
            base_path,
        )
        logging.info(f"Setup stdout: {await setup_teardown_container.stdout()}")
    yield None
    if client_container and hasattr(client_container_config, "teardown_command") and client_container_config.teardown_command:
        logging.info("Running teardown")
        setup_teardown_container = await client_container_runner.do_teardown(
            client_container,
            client_container_config.teardown_command,
        )
        logging.info(f"Teardown stdout: {await setup_teardown_container.stdout()}")


@pytest.fixture(scope="session")
async def final_teardown(
    client_container_config_global: Optional[ClientContainerConfig],
    client_final_teardown_container: Optional[dagger.Container],
):
    yield
    if client_final_teardown_container and client_container_config_global:
        logging.info("Doing final teardown.")
        if hasattr(client_container_config_global, "final_teardown_command"):
            setup_teardown_container = await client_container_runner.do_teardown(
                client_final_teardown_container,
                client_container_config_global.final_teardown_command,
            )
            logging.info(f"Final teardown stdout: {await setup_teardown_container.stdout()}")


@pytest.fixture(name="previous_connector_image_name")
def previous_connector_image_name_fixture(image_tag, inputs) -> str:
    """Fixture with previous connector image name to use for backward compatibility tests"""
    return f"{image_tag.split(':')[0]}:{inputs.backward_compatibility_tests_config.previous_connector_version}"


@pytest.fixture()
async def previous_version_connector_container(
    dagger_client,
    previous_connector_image_name,
):
    connector_container = await connector_runner.get_connector_container(dagger_client, previous_connector_image_name)
    if cachebuster := os.environ.get("CACHEBUSTER"):
        connector_container = connector_container.with_env_variable("CACHEBUSTER", cachebuster)
    return await connector_container


@pytest.fixture(name="previous_connector_docker_runner")
async def previous_connector_docker_runner_fixture(
    previous_version_connector_container, deployment_mode
) -> connector_runner.ConnectorRunner:
    """Fixture to create a connector runner with the previous connector docker image.
    Returns None if the latest image was not found, to skip downstream tests if the current connector is not yet published to the docker registry.
    Raise not found error if the previous connector image is not latest and expected to be published.
    """
    return connector_runner.ConnectorRunner(previous_version_connector_container, deployment_mode=deployment_mode)


@pytest.fixture(name="empty_streams")
def empty_streams_fixture(inputs, test_strictness_level) -> Set[EmptyStreamConfiguration]:
    empty_streams = getattr(inputs, "empty_streams", set())
    if test_strictness_level is Config.TestStrictnessLevel.high and empty_streams:
        all_empty_streams_have_bypass_reasons = all([bool(empty_stream.bypass_reason) for empty_stream in inputs.empty_streams])
        if not all_empty_streams_have_bypass_reasons:
            pytest.fail("A bypass_reason must be filled in for all empty streams when test_strictness_level is set to high.")
    return empty_streams


@pytest.fixture(name="ignored_fields")
def ignored_fields_fixture(inputs, test_strictness_level) -> Optional[Mapping[str, List[IgnoredFieldsConfiguration]]]:
    ignored_fields = getattr(inputs, "ignored_fields", {}) or {}
    if test_strictness_level is Config.TestStrictnessLevel.high and ignored_fields:
        all_ignored_fields_have_bypass_reasons = all(
            [bool(ignored_field.bypass_reason) for ignored_field in itertools.chain.from_iterable(inputs.ignored_fields.values())]
        )
        if not all_ignored_fields_have_bypass_reasons:
            pytest.fail("A bypass_reason must be filled in for all ignored fields when test_strictness_level is set to high.")
    return ignored_fields


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


@pytest.fixture(name="discovered_catalog")
async def discovered_catalog_fixture(
    connector_config,
    docker_runner: connector_runner.ConnectorRunner,
) -> MutableMapping[str, AirbyteStream]:
    """JSON schemas for each stream"""

    output = await docker_runner.call_discover(config=connector_config)
    catalogs = [message.catalog for message in output if message.type == Type.CATALOG]
    if len(catalogs) == 0:
        raise ValueError("No catalog message was emitted")
    return {stream.name: stream for stream in catalogs[-1].streams}


@pytest.fixture(name="previous_discovered_catalog")
async def previous_discovered_catalog_fixture(
    connector_config,
    previous_connector_image_name,
    previous_connector_docker_runner: connector_runner.ConnectorRunner,
) -> MutableMapping[str, AirbyteStream]:
    """JSON schemas for each stream"""
    if previous_connector_docker_runner is None:
        logging.warning(
            f"\n We could not retrieve the previous discovered catalog as a connector runner for the previous connector version ({previous_connector_image_name}) could not be instantiated."
        )
        return None
    try:
        output = await previous_connector_docker_runner.call_discover(config=connector_config)
    except dagger.DaggerError:
        logging.warning(
            "\n DISCOVER on the previous connector version failed. This could be because the current connector config is not compatible with the previous connector version."
        )
        return None
    catalogs = [message.catalog for message in output if message.type == Type.CATALOG]
    if len(catalogs) == 0:
        raise ValueError("No catalog message was emitted")
    return {stream.name: stream for stream in catalogs[-1].streams}


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
    logger.log_json_list = lambda line: logger.info(json.dumps(list(line), indent=1))
    logger.handlers = [fh]
    return logger


@pytest.fixture(name="actual_connector_spec")
async def actual_connector_spec_fixture(docker_runner: connector_runner.ConnectorRunner) -> ConnectorSpecification:
    output = await docker_runner.call_spec()
    spec_messages = filter_output(output, Type.SPEC)
    assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
    return spec_messages[0].spec


@pytest.fixture(name="previous_connector_spec")
async def previous_connector_spec_fixture(
    request: BaseTest, previous_connector_docker_runner: connector_runner.ConnectorRunner
) -> Optional[ConnectorSpecification]:
    if previous_connector_docker_runner is None:
        logging.warning(
            "\n We could not retrieve the previous connector spec as a connector runner for the previous connector version could not be instantiated."
        )
        return None
    output = await previous_connector_docker_runner.call_spec()
    spec_messages = filter_output(output, Type.SPEC)
    assert len(spec_messages) == 1, "Spec message should be emitted exactly once"
    return spec_messages[0].spec


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
            f"{session.startdir} - Connector Acceptance Test run - "
            # using subprocess.check_output to run cmd to get git hash
            f"{check_output('git rev-parse HEAD', stderr=STDOUT, shell=True).decode('ascii').strip()}"
            f" - {result}"
        )
    except Exception as e:
        logger.info(e)  # debug
        pass


@pytest.fixture(name="connector_metadata")
def connector_metadata_fixture(base_path) -> dict:
    return load_yaml_or_json_path(base_path / "metadata.yaml")


@pytest.fixture(name="docs_path")
def docs_path_fixture(base_path, connector_metadata) -> Path:
    path_to_docs = connector_metadata["data"]["documentationUrl"].replace("https://docs.airbyte.com", "docs") + ".md"
    airbyte_path = Path(base_path).parents[6]
    return airbyte_path / path_to_docs


@pytest.fixture(name="connector_documentation")
def connector_documentation_fixture(docs_path: str) -> str:
    with open(docs_path, "r") as f:
        return f.read().rstrip()


@pytest.fixture(name="is_connector_certified")
def connector_certification_status_fixture(connector_metadata: dict) -> bool:
    return connector_metadata.get("data", {}).get("ab_internal", {}).get("ql", 0) >= 400
