# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, AsyncIterable, Callable, Dict, List, Optional

import dagger
import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog  # type: ignore
from live_tests.commons.connection_objects_retrieval import ConnectionObject, get_connection_objects
from live_tests.commons.connector_runner import ConnectorRunner
from live_tests.commons.models import (
    Command,
    ConnectionObjects,
    ConnectorUnderTest,
    ExecutionInputs,
    ExecutionReport,
    ExecutionResult,
    SecretDict,
)
from live_tests.commons.utils import get_connector_under_test

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.fixtures import SubRequest
    from pytest_sugar import SugarTerminalReporter  # type: ignore

## CONSTS
LOGGER = logging.getLogger("regression_tests")
MAIN_OUTPUT_DIRECTORY = Path("/tmp/regression_tests_artifacts")

# It's used by Dagger and its very verbose
logging.getLogger("httpx").setLevel(logging.ERROR)

## STASH KEYS
SESSION_START_TIMESTAMP = pytest.StashKey[int]()
TEST_ARTIFACT_DIRECTORY = pytest.StashKey[Path]()
DAGGER_LOG_PATH = pytest.StashKey[Path]()


## PYTEST HOOKS
def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--connector-image",
        help="The connector image name on which the regressions tests will run: e.g. airbyte/source-faker",
    )
    parser.addoption(
        "--control-version",
        default="latest",
        help="The control version used for regression testing. Defaults to latest",
    )
    parser.addoption(
        "--target-version",
        default="dev",
        help="The target version used for regression testing. Defaults to latest",
    )
    parser.addoption(
        "--deny-confirmation",
        default=False,
        help="Always deny confirmation prompts. Useful for test development. Defaults to False",
    )
    parser.addoption("--config-path")
    parser.addoption("--catalog-path")
    parser.addoption("--state-path")
    parser.addoption("--connection-id")


def pytest_configure(config: Config) -> None:
    start_timestamp = int(time.time())
    test_artifacts_directory = MAIN_OUTPUT_DIRECTORY / f"session_{start_timestamp}"
    test_artifacts_directory.mkdir(parents=True, exist_ok=True)
    dagger_log_path = test_artifacts_directory / "dagger.log"
    config.stash[SESSION_START_TIMESTAMP] = start_timestamp
    config.stash[TEST_ARTIFACT_DIRECTORY] = test_artifacts_directory
    dagger_log_path.touch()
    config.stash[DAGGER_LOG_PATH] = dagger_log_path


def pytest_terminal_summary(terminalreporter: SugarTerminalReporter, exitstatus: int, config: Config) -> None:
    terminalreporter.ensure_newline()
    terminalreporter.section("Test artifacts", sep="=", bold=True, blue=True)
    terminalreporter.line(f"All tests artifacts for this sessions should be available in {config.stash[TEST_ARTIFACT_DIRECTORY].resolve()}")
    terminalreporter.section("Dagger logs", sep=".")
    terminalreporter.line(f"Dagger logs are stored in {config.stash[DAGGER_LOG_PATH]}")
    artifact_subsection: Dict[str, List[str]] = {}
    for report in terminalreporter.reports:
        properties_dict = {
            record_property_key: record_property_value for record_property_key, record_property_value in report.user_properties
        }
        if "control_execution_report" in properties_dict or "target_execution_report" in properties_dict:
            artifact_subsection[report.head_line] = []
            if "control_execution_report" in properties_dict:
                artifact_subsection[report.head_line].append(
                    f"Control execution artifacts stored in {properties_dict['control_execution_report'].saved_path}"
                )
            if "target_execution_report" in properties_dict:
                artifact_subsection[report.head_line].append(
                    f"Target execution artifacts stored in {properties_dict['target_execution_report'].saved_path}"
                )

    if artifact_subsection:
        terminalreporter.ensure_newline()
        for section, artifact_lines in artifact_subsection.items():
            terminalreporter.ensure_newline()
            terminalreporter.section(section, sep=".")
            terminalreporter.line(os.linesep.join(artifact_lines))


## HELPERS
async def persist_report(
    request: SubRequest,
    output_directory: Path,
    execution_inputs: ExecutionInputs,
    execution_result: ExecutionResult,
    session_start_timestamp: int,
) -> ExecutionReport:
    test_name = request.node.name
    test_output_directory = Path(output_directory / test_name)
    test_output_directory.mkdir(parents=True, exist_ok=True)
    report = ExecutionReport(execution_inputs, execution_result, created_at=session_start_timestamp)
    await report.save_to_disk(test_output_directory)
    LOGGER.info(f"Execution report saved to {test_output_directory}")
    return report


def get_option_or_fail(request: SubRequest, option: str) -> str:
    if option_value := request.config.getoption(option):
        return option_value
    pytest.fail(f"Missing required option: {option}")


def ask_for_confirmation(message: str, always_deny: bool = False) -> None:
    if always_deny:
        pytest.skip("Skipped by user.")
    if not os.environ.get("CI"):
        if not input(f"{message}. Do you want to continue? [y/N]: ").lower().strip() == "y":
            pytest.skip("Skipped by user.")


## FIXTURES


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def session_start_timestamp(request: SubRequest) -> int:
    return request.config.stash[SESSION_START_TIMESTAMP]


@pytest.fixture(scope="session")
def test_artifacts_directory(request: SubRequest) -> Path:
    return request.config.stash[TEST_ARTIFACT_DIRECTORY]


@pytest.fixture(scope="session")
def deny_confirmation(request: SubRequest) -> bool:
    return bool(request.config.getoption("--deny-confirmation"))


@pytest.fixture(scope="session")
def connector_image(request: SubRequest) -> str:
    return get_option_or_fail(request, "--connector-image")


@pytest.fixture(scope="session")
def control_version(request: SubRequest) -> str:
    return get_option_or_fail(request, "--control-version")


@pytest.fixture(scope="session")
def target_version(control_version: str, request: SubRequest) -> str:
    target_version = get_option_or_fail(request, "--target-version")
    if target_version == control_version:
        pytest.fail(f"Control and target versions are the same: {control_version}. Please provide different versions.")
    return target_version


@pytest.fixture(scope="session")
def connection_id(request: SubRequest) -> Optional[str]:
    return request.config.getoption("--connection-id")


@pytest.fixture(scope="session")
def custom_source_config_path(request: SubRequest) -> Optional[Path]:
    if config_path := request.config.getoption("--config-path"):
        return Path(config_path)
    return None


@pytest.fixture(scope="session")
def custom_catalog_path(request: SubRequest) -> Optional[Path]:
    if catalog_path := request.config.getoption("--catalog-path"):
        return Path(catalog_path)
    return None


@pytest.fixture(scope="session")
def custom_state_path(request: SubRequest) -> Optional[Path]:
    if state_path := request.config.getoption("--state-path"):
        return Path(state_path)
    return None


@pytest.fixture(scope="session")
def retrieval_reason(
    connection_id: Optional[str],
    connector_image: str,
    control_version: str,
    target_version: str,
) -> Optional[str]:
    if connection_id:
        return f"Running regression tests on connection {connection_id} for connector {connector_image} on the control ({control_version}) and target versions ({target_version})."
    return None


@pytest.fixture(scope="session")
def connection_objects(
    connection_id: Optional[str],
    custom_source_config_path: Optional[Path],
    custom_catalog_path: Optional[Path],
    custom_state_path: Optional[Path],
    retrieval_reason: Optional[str],
) -> ConnectionObjects:
    return get_connection_objects(
        {
            ConnectionObject.SOURCE_CONFIG,
            ConnectionObject.CONFIGURED_CATALOG,
            ConnectionObject.STATE,
        },
        connection_id,
        custom_source_config_path,
        custom_catalog_path,
        custom_state_path,
        retrieval_reason,
    )


@pytest.fixture(scope="session")
def connector_config(connection_objects: ConnectionObjects) -> Optional[SecretDict]:
    return connection_objects.source_config


@pytest.fixture(scope="session")
def catalog(
    connection_objects: ConnectionObjects,
) -> Optional[ConfiguredAirbyteCatalog]:
    return connection_objects.catalog


@pytest.fixture(scope="session")
def state(connection_objects: ConnectionObjects) -> Optional[Dict]:
    return connection_objects.state


@pytest.fixture(scope="session")
def dagger_connection(request: SubRequest) -> dagger.Connection:
    return dagger.Connection(dagger.Config(log_output=request.config.stash[DAGGER_LOG_PATH].open("w")))


@pytest.fixture(scope="session")
async def dagger_client(
    dagger_connection: dagger.Connection,
) -> AsyncIterable[dagger.Client]:
    async with dagger_connection as client:
        yield client


@pytest.fixture(scope="session")
async def control_connector(dagger_client: dagger.Client, connector_image: str, control_version: str) -> ConnectorUnderTest:
    return await get_connector_under_test(dagger_client, f"{connector_image}:{control_version}")


@pytest.fixture(scope="session")
async def target_connector(dagger_client: dagger.Client, connector_image: str, target_version: str) -> ConnectorUnderTest:
    return await get_connector_under_test(dagger_client, f"{connector_image}:{target_version}")


@pytest.fixture
def spec_control_execution_inputs(
    control_connector: ConnectorUnderTest,
) -> ExecutionInputs:
    return ExecutionInputs(connector_under_test=control_connector, command=Command.SPEC)


@pytest.fixture
def spec_control_connector_runner(dagger_client: dagger.Client, spec_control_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **spec_control_execution_inputs.to_dict())


@pytest.fixture
async def spec_control_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    spec_control_execution_inputs: ExecutionInputs,
    spec_control_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
) -> ExecutionResult:
    logging.info(f"Running spec for control connector {spec_control_execution_inputs.connector_under_test.name}")
    execution_result = await spec_control_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        spec_control_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("control_execution_report", execution_report)
    return execution_result


@pytest.fixture
def spec_target_execution_inputs(
    target_connector: ConnectorUnderTest,
) -> ExecutionInputs:
    return ExecutionInputs(connector_under_test=target_connector, command=Command.SPEC)


@pytest.fixture
def spec_target_connector_runner(dagger_client: dagger.Client, spec_target_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **spec_target_execution_inputs.to_dict())


@pytest.fixture
async def spec_target_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    spec_control_execution_result: ExecutionResult,
    spec_target_execution_inputs: ExecutionInputs,
    spec_target_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
) -> ExecutionResult:
    logging.info(f"Running spec for target connector {spec_target_execution_inputs.connector_under_test.name}")
    execution_result = await spec_target_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        spec_target_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("target_execution_report", execution_report)
    return execution_result


@pytest.fixture
def check_control_execution_inputs(control_connector: ConnectorUnderTest, connector_config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.CHECK,
        config=connector_config,
    )


@pytest.fixture
def check_control_connector_runner(dagger_client: dagger.Client, check_control_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **check_control_execution_inputs.to_dict())


@pytest.fixture
async def check_control_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    check_control_execution_inputs: ExecutionInputs,
    check_control_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
) -> ExecutionResult:
    logging.info(f"Running check for control connector {check_control_execution_inputs.connector_under_test.name}")
    execution_result = await check_control_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        check_control_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("control_execution_report", execution_report)
    return execution_result


@pytest.fixture
def check_target_execution_inputs(target_connector: ConnectorUnderTest, connector_config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.CHECK,
        config=connector_config,
    )


@pytest.fixture
def check_target_connector_runner(dagger_client: dagger.Client, check_target_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **check_target_execution_inputs.to_dict())


@pytest.fixture
async def check_target_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    check_control_execution_result: ExecutionResult,
    check_target_execution_inputs: ExecutionInputs,
    check_target_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
) -> ExecutionResult:
    logging.info(f"Running check for target connector {check_target_execution_inputs.connector_under_test.name}")
    execution_result = await check_target_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        check_target_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("target_execution_report", execution_report)
    return execution_result


@pytest.fixture
def discover_control_execution_inputs(control_connector: ConnectorUnderTest, connector_config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.DISCOVER,
        config=connector_config,
    )


@pytest.fixture
async def discover_control_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    discover_control_execution_inputs: ExecutionInputs,
    discover_control_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
) -> ExecutionResult:
    logging.info(f"Running discover for control connector {discover_control_execution_inputs.connector_under_test.name}")
    execution_result = await discover_control_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        discover_control_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("control_execution_report", execution_report)
    return execution_result


@pytest.fixture
def discover_target_execution_inputs(target_connector: ConnectorUnderTest, connector_config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.DISCOVER,
        config=connector_config,
    )


@pytest.fixture
def discover_control_connector_runner(dagger_client: dagger.Client, discover_control_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **discover_control_execution_inputs.to_dict())


@pytest.fixture
def discover_target_connector_runner(dagger_client: dagger.Client, discover_target_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **discover_target_execution_inputs.to_dict())


@pytest.fixture
async def discover_target_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    discover_control_execution_result: ExecutionResult,
    discover_target_execution_inputs: ExecutionInputs,
    discover_target_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
) -> ExecutionResult:
    logging.info(f"Running discover for target connector {discover_target_execution_inputs.connector_under_test.name}")
    execution_result = await discover_target_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        discover_target_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("target_execution_report", execution_report)
    return execution_result


@pytest.fixture
def read_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    connector_config: SecretDict,
    catalog: ConfiguredAirbyteCatalog,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.READ,
        catalog=catalog,
        config=connector_config,
    )


@pytest.fixture
def read_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    connector_config: SecretDict,
    catalog: ConfiguredAirbyteCatalog,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.READ,
        catalog=catalog,
        config=connector_config,
    )


@pytest.fixture
def read_control_connector_runner(dagger_client: dagger.Client, read_control_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **read_control_execution_inputs.to_dict())


@pytest.fixture
async def read_control_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    read_control_execution_inputs: ExecutionInputs,
    read_control_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
    deny_confirmation: bool,
) -> ExecutionResult:
    ask_for_confirmation(
        f"{request.node.name} will run a full refresh read on control connector. It might induce rate limits or costs on source",
        deny_confirmation,
    )
    logging.info(f"Running read for control connector {read_control_execution_inputs.connector_under_test.name}")
    execution_result = await read_control_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        read_control_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("control_execution_report", execution_report)
    return execution_result


@pytest.fixture
def read_target_connector_runner(dagger_client: dagger.Client, read_target_execution_inputs: ExecutionInputs) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **read_target_execution_inputs.to_dict())


@pytest.fixture
async def read_target_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    read_control_execution_result: ExecutionResult,
    read_target_execution_inputs: ExecutionInputs,
    read_target_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
    deny_confirmation: bool,
) -> ExecutionResult:
    ask_for_confirmation(
        f"{request.node.name} will run a full refresh read on target connector. It might induce rate limits or costs on source",
        deny_confirmation,
    )
    logging.info(f"Running read for target connector {read_target_execution_inputs.connector_under_test.name}")
    execution_result = await read_target_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        read_target_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("target_execution_report", execution_report)
    return execution_result


@pytest.fixture
def read_with_state_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    connector_config: SecretDict,
    catalog: ConfiguredAirbyteCatalog,
    state: dict,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.READ_WITH_STATE,
        catalog=catalog,
        config=connector_config,
        state=state,
    )


@pytest.fixture
def read_with_state_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    connector_config: SecretDict,
    catalog: ConfiguredAirbyteCatalog,
    state: dict,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.READ_WITH_STATE,
        catalog=catalog,
        config=connector_config,
        state=state,
    )


@pytest.fixture
def read_with_state_control_connector_runner(
    dagger_client: dagger.Client,
    read_with_state_control_execution_inputs: ExecutionInputs,
) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **read_with_state_control_execution_inputs.to_dict())


@pytest.fixture
async def read_with_state_control_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    read_with_state_control_execution_inputs: ExecutionInputs,
    read_with_state_control_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
    deny_confirmation: bool,
) -> ExecutionResult:
    ask_for_confirmation(
        f"{request.node.name} will run an incremental read on control connector. It might induce rate limits or costs on source",
        deny_confirmation,
    )
    logging.info(f"Running read with state for control connector {read_with_state_control_execution_inputs.connector_under_test.name}")
    execution_result = await read_with_state_control_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        read_with_state_control_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("control_execution_report", execution_report)
    return execution_result


@pytest.fixture
def read_with_state_target_connector_runner(
    dagger_client: dagger.Client,
    read_with_state_target_execution_inputs: ExecutionInputs,
) -> ConnectorRunner:
    return ConnectorRunner(dagger_client, **read_with_state_target_execution_inputs.to_dict())


@pytest.fixture
async def read_with_state_target_execution_result(
    record_property: Callable,
    request: SubRequest,
    test_artifacts_directory: Path,
    read_with_state_control_execution_result: ExecutionResult,
    read_with_state_target_execution_inputs: ExecutionInputs,
    read_with_state_target_connector_runner: ConnectorRunner,
    session_start_timestamp: int,
    deny_confirmation: bool,
) -> ExecutionResult:
    ask_for_confirmation(
        f"{request.node.name} will run an incremental read on target connector. It might induce rate limits or costs on source",
        deny_confirmation,
    )
    logging.info(f"Running read with state for target connector {read_with_state_target_execution_inputs.connector_under_test.name}")
    execution_result = await read_with_state_target_connector_runner.run()
    execution_report = await persist_report(
        request,
        test_artifacts_directory,
        read_with_state_target_execution_inputs,
        execution_result,
        session_start_timestamp,
    )
    record_property("target_execution_report", execution_report)
    return execution_result
