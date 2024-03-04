import pytest
from live_tests.commons.models import ConnectorUnderTest, ExecutionInputs, Command, SecretDict, ExecutionResult, ExecutionReport
from live_tests.commons.utils import get_connector_under_test, get_connector_config, get_state
from live_tests.commons.connector_runner import ConnectorRunner
import sys
import dagger
from typing import AsyncGenerator, Optional
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from _pytest.fixtures import SubRequest
from pathlib import Path
import logging
import time

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

def pytest_addoption(parser):
    parser.addoption(
        "--output-directory", default=".", help="Path to a directory where the test execution reports will be stored"
    )
    parser.addoption(
        "--connector-image", help="The connector image name on which the regressions tests will run: e.g. airbyte/source-faker"
    )
    parser.addoption(
         "--control-version", default="latest", help="The control version used for regression testing. Defaults to latest"
    )
    parser.addoption(
         "--target-version", default="dev", help="The target version used for regression testing. Defaults to latest"
    )
    parser.addoption(
        "--config-path"
    )
    parser.addoption(
        "--catalog-path"
    )
    parser.addoption(
        "--state-path"
    )

def get_option_or_fail(request: SubRequest, option: str):
    if option_value := request.config.getoption(option):
        return option_value
    pytest.fail(f"Missing required option: {option}")

def persist_report(request, output_directory, execution_inputs, execution_results, session_start_timestamp) -> ExecutionReport:
    test_name = request.node.name
    test_output_directory =  Path(output_directory / test_name)
    test_output_directory.mkdir(parents=True, exist_ok=True)
    report = ExecutionReport(execution_inputs, execution_results, created_at=session_start_timestamp)
    saved_files = report.save_to_disk(test_output_directory)
    for file_path in saved_files:
        LOGGER.info(f"Saved {file_path}")
    return report

@pytest.fixture(scope="session")
def session_start_timestamp() -> int:
    return int(time.time())

@pytest.fixture(scope="session")
def output_directory(request: SubRequest) -> Path:
    return Path(get_option_or_fail(request, "--output-directory"))

@pytest.fixture(scope="session")
def connector_image(request: SubRequest) -> str:
    return get_option_or_fail(request, "--connector-image")

@pytest.fixture(scope="session")
def control_version(request: SubRequest) -> str:
    return get_option_or_fail(request, "--control-version")


@pytest.fixture(scope="session")
def target_version(request: SubRequest) -> str:
    return get_option_or_fail(request, "--target-version")

@pytest.fixture(scope="session")
def catalog(request: SubRequest) -> Optional[ConfiguredAirbyteCatalog]:
    catalog_path = get_option_or_fail(request, "--catalog-path")
    return ConfiguredAirbyteCatalog.parse_file(catalog_path) if catalog_path else None

@pytest.fixture(scope="session")
def config(request: SubRequest) -> Optional[SecretDict]:

    return get_connector_config(get_option_or_fail(request, "--config-path"))

@pytest.fixture(scope="session")
def state(request: SubRequest) -> Optional[dict]:
    return get_state(get_option_or_fail(request, "--state-path"))

@pytest.fixture(scope="session")
def dagger_connection() -> dagger.Connection:
    return dagger.Connection(dagger.Config(log_output=sys.stderr))


@pytest.fixture(scope="session")
async def dagger_client(dagger_connection: dagger.Connection):
    async with dagger_connection as client:
        yield client


@pytest.fixture(scope="session")
async def control_connector(dagger_client: dagger.Client, connector_image, control_version) -> ConnectorUnderTest:
    return await get_connector_under_test(dagger_client, f"{connector_image}:{control_version}")

@pytest.fixture(scope="session")
async def target_connector(dagger_client, connector_image, target_version) -> ConnectorUnderTest:
    return await get_connector_under_test(dagger_client, f"{connector_image}:{target_version}")

@pytest.fixture
def spec_control_execution_inputs(control_connector: ConnectorUnderTest) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.SPEC
    )

@pytest.fixture
def spec_target_execution_inputs(target_connector: ConnectorUnderTest) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.SPEC
    )

@pytest.fixture
def spec_control_connector_runner(dagger_client, spec_control_execution_inputs):
    return ConnectorRunner(dagger_client, **spec_control_execution_inputs.to_dict())

@pytest.fixture
def spec_target_connector_runner(dagger_client, spec_target_execution_inputs):
    return ConnectorRunner(dagger_client, **spec_target_execution_inputs.to_dict())


@pytest.fixture
def check_control_execution_inputs(control_connector: ConnectorUnderTest, config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.CHECK,
        config=config
    )

@pytest.fixture
def check_target_execution_inputs(target_connector: ConnectorUnderTest, config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.CHECK,
        config=config
    )


@pytest.fixture
def check_control_connector_runner(dagger_client, check_control_execution_inputs):
    return ConnectorRunner(dagger_client, **check_control_execution_inputs.to_dict())

@pytest.fixture
def check_target_connector_runner(dagger_client, check_target_execution_inputs):
    return ConnectorRunner(dagger_client, **check_target_execution_inputs.to_dict())


@pytest.fixture
def discover_control_execution_inputs(control_connector: ConnectorUnderTest, config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.DISCOVER,
        config=config
    )

@pytest.fixture
def discover_target_execution_inputs(target_connector: ConnectorUnderTest, config: SecretDict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.DISCOVER,
        config=config
    )

@pytest.fixture
def discover_control_connector_runner(dagger_client, discover_control_execution_inputs):
    return ConnectorRunner(dagger_client, **discover_control_execution_inputs.to_dict())

@pytest.fixture
def discover_target_connector_runner(dagger_client, discover_target_execution_inputs):
    return ConnectorRunner(dagger_client, **discover_target_execution_inputs.to_dict())


@pytest.fixture
def read_control_execution_inputs(control_connector: ConnectorUnderTest, config: SecretDict, catalog: ConfiguredAirbyteCatalog) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.READ,
        catalog=catalog,
        config=config
    )

@pytest.fixture
def read_target_execution_inputs(target_connector: ConnectorUnderTest, config: SecretDict, catalog: ConfiguredAirbyteCatalog) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.READ,
        catalog=catalog,
        config=config
    )


@pytest.fixture
def read_control_connector_runner(dagger_client, read_control_execution_inputs):
    return ConnectorRunner(dagger_client, **read_control_execution_inputs.to_dict())

@pytest.fixture
async def read_control_execution_result(request, output_directory, read_control_execution_inputs, read_control_connector_runner, session_start_timestamp):
    execution_results = await read_control_connector_runner.run()
    yield execution_results
    execution_report = persist_report(request, output_directory, read_control_execution_inputs, execution_results, session_start_timestamp)

@pytest.fixture
def read_target_connector_runner(dagger_client, read_target_execution_inputs):
    return ConnectorRunner(dagger_client, **read_target_execution_inputs.to_dict())

@pytest.fixture
# Depend on read_control_execution_result to leverage HTTP caching 
async def read_target_execution_result(request, output_directory, read_control_execution_result, read_target_execution_inputs, read_target_connector_runner, session_start_timestamp):
    execution_results = await read_target_connector_runner.run()
    yield execution_results
    execution_report = persist_report(request, output_directory, read_target_execution_inputs, execution_results, session_start_timestamp)

@pytest.fixture
def read_with_state_control_execution_inputs(control_connector: ConnectorUnderTest, config: SecretDict, catalog: ConfiguredAirbyteCatalog, state: dict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        command=Command.READ_WITH_STATE,
        catalog=catalog,
        config=config,
        state=state
    )

@pytest.fixture
def read_with_state_target_execution_inputs(target_connector: ConnectorUnderTest, config: SecretDict, catalog: ConfiguredAirbyteCatalog, state: dict) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        command=Command.READ_WITH_STATE,
        catalog=catalog,
        config=config,
        state=state
    )


@pytest.fixture
def read_with_state_control_connector_runner(dagger_client, read_with_state_control_execution_inputs):
    return ConnectorRunner(dagger_client, **read_with_state_control_execution_inputs.to_dict())

@pytest.fixture
def read_with_state_target_connector_runner(dagger_client, read_with_state_target_execution_inputs):
    return ConnectorRunner(dagger_client, **read_with_state_target_execution_inputs.to_dict())
