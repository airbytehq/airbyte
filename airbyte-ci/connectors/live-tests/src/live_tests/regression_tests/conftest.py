# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import logging
import os
import textwrap
import time
import webbrowser
from collections.abc import AsyncGenerator, AsyncIterable, Callable, Generator, Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import dagger
import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog  # type: ignore
from connection_retriever.audit_logging import get_user_email  # type: ignore
from connection_retriever.retrieval import ConnectionNotFoundError, NotPermittedError  # type: ignore
from live_tests.commons.connection_objects_retrieval import ConnectionObject, get_connection_objects
from live_tests.commons.connector_runner import ConnectorRunner, Proxy
from live_tests.commons.models import (
    ActorType,
    Command,
    ConnectionObjects,
    ConnectorUnderTest,
    ExecutionInputs,
    ExecutionResult,
    SecretDict,
    TargetOrControl,
)
from live_tests.commons.secret_access import get_airbyte_api_key
from live_tests.commons.segment_tracking import track_usage
from live_tests.commons.utils import build_connection_url, clean_up_artifacts
from live_tests.regression_tests import stash_keys
from rich.prompt import Confirm, Prompt

from .report import Report, ReportState

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


## PYTEST HOOKS
def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--connector-image",
        help="The connector image name on which the regressions tests will run: e.g. airbyte/source-faker",
    )
    parser.addoption(
        "--control-version",
        help="The control version used for regression testing.",
    )
    parser.addoption(
        "--target-version",
        default="dev",
        help="The target version used for regression testing. Defaults to dev.",
    )
    parser.addoption("--config-path")
    parser.addoption("--catalog-path")
    parser.addoption("--state-path")
    parser.addoption("--connection-id")
    parser.addoption("--pr-url", help="The URL of the PR you are testing")
    parser.addoption(
        "--stream",
        help="The stream to run the tests on. (Can be used multiple times)",
        action="append",
    )
    # Required when running in CI
    parser.addoption("--run-id", type=str)
    parser.addoption(
        "--should-read-with-state",
        type=bool,
        help="Whether to run the `read` command with state. \n"
        "We recommend reading with state to properly test incremental sync. \n"
        "But if the target version introduces a breaking change in the state, you might want to run without state. \n",
    )


def pytest_configure(config: Config) -> None:
    user_email = get_user_email()
    config.stash[stash_keys.RUN_IN_AIRBYTE_CI] = bool(os.getenv("RUN_IN_AIRBYTE_CI", False))
    config.stash[stash_keys.IS_PRODUCTION_CI] = bool(os.getenv("CI", False))

    if not config.stash[stash_keys.RUN_IN_AIRBYTE_CI]:
        prompt_for_confirmation(user_email)

    track_usage(
        "production-ci"
        if config.stash[stash_keys.IS_PRODUCTION_CI]
        else "local-ci"
        if config.stash[stash_keys.RUN_IN_AIRBYTE_CI]
        else user_email,
        vars(config.option),
    )
    config.stash[stash_keys.AIRBYTE_API_KEY] = get_airbyte_api_key()
    config.stash[stash_keys.USER] = user_email
    config.stash[stash_keys.SESSION_RUN_ID] = config.getoption("--run-id") or str(int(time.time()))
    test_artifacts_directory = get_artifacts_directory(config)
    duckdb_path = test_artifacts_directory / "duckdb.db"
    config.stash[stash_keys.DUCKDB_PATH] = duckdb_path
    test_artifacts_directory.mkdir(parents=True, exist_ok=True)
    dagger_log_path = test_artifacts_directory / "dagger.log"
    config.stash[stash_keys.IS_PERMITTED_BOOL] = False
    report_path = test_artifacts_directory / "report.html"

    config.stash[stash_keys.TEST_ARTIFACT_DIRECTORY] = test_artifacts_directory
    dagger_log_path.touch()
    config.stash[stash_keys.DAGGER_LOG_PATH] = dagger_log_path
    config.stash[stash_keys.PR_URL] = get_option_or_fail(config, "--pr-url")
    _connection_id = config.getoption("--connection-id")
    config.stash[stash_keys.AUTO_SELECT_CONNECTION] = _connection_id == "auto"
    config.stash[stash_keys.CONNECTOR_IMAGE] = get_option_or_fail(config, "--connector-image")
    config.stash[stash_keys.TARGET_VERSION] = get_option_or_fail(config, "--target-version")
    custom_source_config_path = config.getoption("--config-path")
    custom_configured_catalog_path = config.getoption("--catalog-path")
    custom_state_path = config.getoption("--state-path")
    config.stash[stash_keys.SELECTED_STREAMS] = set(config.getoption("--stream") or [])

    if config.stash[stash_keys.RUN_IN_AIRBYTE_CI]:
        config.stash[stash_keys.SHOULD_READ_WITH_STATE] = bool(get_option_or_fail(config, "--should-read-with-state"))
    elif _should_read_with_state := config.getoption("--should-read-with-state"):
        config.stash[stash_keys.SHOULD_READ_WITH_STATE] = _should_read_with_state
    else:
        config.stash[stash_keys.SHOULD_READ_WITH_STATE] = prompt_for_read_with_or_without_state()

    retrieval_reason = f"Running regression tests on connection for connector {config.stash[stash_keys.CONNECTOR_IMAGE]} on target versions ({config.stash[stash_keys.TARGET_VERSION]})."

    try:
        config.stash[stash_keys.CONNECTION_OBJECTS] = get_connection_objects(
            {
                ConnectionObject.SOURCE_CONFIG,
                ConnectionObject.CATALOG,
                ConnectionObject.CONFIGURED_CATALOG,
                ConnectionObject.STATE,
                ConnectionObject.WORKSPACE_ID,
                ConnectionObject.SOURCE_DOCKER_IMAGE,
                ConnectionObject.SOURCE_ID,
                ConnectionObject.DESTINATION_ID,
            },
            None if _connection_id == "auto" else _connection_id,
            Path(custom_source_config_path) if custom_source_config_path else None,
            Path(custom_configured_catalog_path) if custom_configured_catalog_path else None,
            Path(custom_state_path) if custom_state_path else None,
            retrieval_reason,
            fail_if_missing_objects=False,
            connector_image=config.stash[stash_keys.CONNECTOR_IMAGE],
            auto_select_connection=config.stash[stash_keys.AUTO_SELECT_CONNECTION],
            selected_streams=config.stash[stash_keys.SELECTED_STREAMS],
        )
        config.stash[stash_keys.IS_PERMITTED_BOOL] = True
    except (ConnectionNotFoundError, NotPermittedError) as exc:
        clean_up_artifacts(MAIN_OUTPUT_DIRECTORY, LOGGER)
        pytest.exit(str(exc))

    config.stash[stash_keys.CONNECTION_ID] = config.stash[stash_keys.CONNECTION_OBJECTS].connection_id  # type: ignore

    if source_docker_image := config.stash[stash_keys.CONNECTION_OBJECTS].source_docker_image:
        config.stash[stash_keys.CONTROL_VERSION] = source_docker_image.split(":")[-1]
    else:
        config.stash[stash_keys.CONTROL_VERSION] = "latest"

    if config.stash[stash_keys.CONTROL_VERSION] == config.stash[stash_keys.TARGET_VERSION]:
        pytest.exit(f"Control and target versions are the same: {control_version}. Please provide different versions.")
    if config.stash[stash_keys.CONNECTION_OBJECTS].workspace_id and config.stash[stash_keys.CONNECTION_ID]:
        config.stash[stash_keys.CONNECTION_URL] = build_connection_url(
            config.stash[stash_keys.CONNECTION_OBJECTS].workspace_id,
            config.stash[stash_keys.CONNECTION_ID],
        )
    else:
        config.stash[stash_keys.CONNECTION_URL] = None
    config.stash[stash_keys.REPORT] = Report(
        report_path,
        config,
    )
    webbrowser.open_new_tab(config.stash[stash_keys.REPORT].path.resolve().as_uri())


def get_artifacts_directory(config: pytest.Config) -> Path:
    run_id = config.stash[stash_keys.SESSION_RUN_ID]
    return MAIN_OUTPUT_DIRECTORY / f"session_{run_id}"


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        if config.stash[stash_keys.SHOULD_READ_WITH_STATE] and "without_state" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="Test is marked with without_state marker"))
        if not config.stash[stash_keys.SHOULD_READ_WITH_STATE] and "with_state" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="Test is marked with with_state marker"))


def pytest_terminal_summary(terminalreporter: SugarTerminalReporter, exitstatus: int, config: Config) -> None:
    config.stash[stash_keys.REPORT].update(ReportState.FINISHED)
    if not config.stash.get(stash_keys.IS_PERMITTED_BOOL, False):
        # Don't display the prompt if the tests were not run due to inability to fetch config
        clean_up_artifacts(MAIN_OUTPUT_DIRECTORY, LOGGER)
        pytest.exit(str(NotPermittedError))

    terminalreporter.ensure_newline()
    terminalreporter.section("Test artifacts", sep="=", bold=True, blue=True)
    terminalreporter.line(
        f"All tests artifacts for this sessions should be available in {config.stash[stash_keys.TEST_ARTIFACT_DIRECTORY].resolve()}"
    )

    if not config.stash[stash_keys.RUN_IN_AIRBYTE_CI]:
        try:
            Prompt.ask(
                textwrap.dedent(
                    """
                    Test artifacts will be destroyed after this prompt.
                    Press enter when you're done reading them.
                    🚨 Do not copy them elsewhere on your disk!!! 🚨
                    """
                )
            )
        finally:
            clean_up_artifacts(MAIN_OUTPUT_DIRECTORY, LOGGER)


def pytest_keyboard_interrupt(excinfo: Exception) -> None:
    LOGGER.error("Test execution was interrupted by the user. Cleaning up test artifacts.")
    clean_up_artifacts(MAIN_OUTPUT_DIRECTORY, LOGGER)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
    outcome = yield
    report = outcome.get_result()
    # This is to add skipped or failed tests due to upstream fixture failures on setup
    if report.outcome in ["failed", "skipped"] or report.when == "call":
        item.config.stash[stash_keys.REPORT].add_test_result(
            report,
            item.function.__doc__,  # type: ignore
        )


## HELPERS


def get_option_or_fail(config: pytest.Config, option: str) -> str:
    if option_value := config.getoption(option):
        return option_value
    pytest.fail(f"Missing required option: {option}")


def prompt_for_confirmation(user_email: str) -> None:
    message = textwrap.dedent(
        f"""
    👮 This program is running on live Airbyte Cloud connection.
    It means that it might induce costs or rate limits on the source.
    This program is storing tests artifacts in {MAIN_OUTPUT_DIRECTORY.resolve()} that you can use for debugging. They will get destroyed after the program execution.

    By approving this prompt, you ({user_email}) confirm that:
    1. You understand the implications of running this test suite.
    2. You have selected the correct target and control versions.
    3. You have selected the right tests according to your testing needs.
    4. You will not copy the test artifacts content.
    5. You want to run the program on the passed connection ID.

    Usage of this tool is tracked and logged.

    Do you want to continue?
    """
    )
    if not os.environ.get("CI") and not Confirm.ask(message):
        pytest.exit("Test execution was interrupted by the user.")


def prompt_for_read_with_or_without_state() -> bool:
    message = textwrap.dedent(
        """
    📖 Do you want to run the read command with or without state?
    1. Run the read command with state
    2. Run the read command without state
                              
    We recommend reading with state to properly test incremental sync.
    But if the target version introduces a breaking change in the state, you might want to run without state.
    """
    )
    return Prompt.ask(message) == "1"


## FIXTURES


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def test_artifacts_directory(request: SubRequest) -> Path:
    return request.config.stash[stash_keys.TEST_ARTIFACT_DIRECTORY]


@pytest.fixture(scope="session")
def connector_image(request: SubRequest) -> str:
    return request.config.stash[stash_keys.CONNECTOR_IMAGE]


@pytest.fixture(scope="session")
def control_version(request: SubRequest) -> str:
    return request.config.stash[stash_keys.CONTROL_VERSION]


@pytest.fixture(scope="session")
def target_version(request: SubRequest) -> str:
    return request.config.stash[stash_keys.TARGET_VERSION]


@pytest.fixture(scope="session")
def connection_id(request: SubRequest) -> Optional[str]:
    return request.config.stash[stash_keys.CONNECTION_ID]


@pytest.fixture(scope="session")
def connection_objects(request: SubRequest) -> ConnectionObjects:
    return request.config.stash[stash_keys.CONNECTION_OBJECTS]


@pytest.fixture(scope="session")
def connector_config(connection_objects: ConnectionObjects) -> Optional[SecretDict]:
    return connection_objects.source_config


@pytest.fixture(scope="session")
def actor_id(connection_objects: ConnectionObjects, control_connector: ConnectorUnderTest) -> str | None:
    if control_connector.actor_type is ActorType.SOURCE:
        return connection_objects.source_id
    elif control_connector.actor_type is ActorType.DESTINATION:
        return connection_objects.destination_id
    else:
        raise ValueError(f"Actor type {control_connector.actor_type} is not supported")


@pytest.fixture(scope="session")
def selected_streams(request: SubRequest) -> set[str]:
    return request.config.stash[stash_keys.SELECTED_STREAMS]


@pytest.fixture(scope="session")
def configured_catalog(connection_objects: ConnectionObjects, selected_streams: Optional[set[str]]) -> ConfiguredAirbyteCatalog:
    if not connection_objects.configured_catalog:
        pytest.skip("Catalog is not provided. The catalog fixture can't be used.")
    assert connection_objects.configured_catalog is not None
    return connection_objects.configured_catalog


@pytest.fixture(scope="session", autouse=True)
def primary_keys_per_stream(
    configured_catalog: ConfiguredAirbyteCatalog,
) -> dict[str, Optional[list[str]]]:
    return {stream.stream.name: stream.primary_key[0] if stream.primary_key else None for stream in configured_catalog.streams}


@pytest.fixture(scope="session")
def configured_streams(
    configured_catalog: ConfiguredAirbyteCatalog,
) -> Iterable[str]:
    return {stream.stream.name for stream in configured_catalog.streams}


@pytest.fixture(scope="session")
def state(connection_objects: ConnectionObjects) -> Optional[dict]:
    return connection_objects.state


@pytest.fixture(scope="session")
def dagger_connection(request: SubRequest) -> dagger.Connection:
    return dagger.Connection(dagger.Config(log_output=request.config.stash[stash_keys.DAGGER_LOG_PATH].open("w")))


@pytest.fixture(scope="session", autouse=True)
async def dagger_client(
    dagger_connection: dagger.Connection,
) -> AsyncIterable[dagger.Client]:
    async with dagger_connection as client:
        yield client


@pytest.fixture(scope="session")
async def control_connector(dagger_client: dagger.Client, connector_image: str, control_version: str) -> ConnectorUnderTest:
    return await ConnectorUnderTest.from_image_name(dagger_client, f"{connector_image}:{control_version}", TargetOrControl.CONTROL)


@pytest.fixture(scope="session")
async def target_connector(dagger_client: dagger.Client, connector_image: str, target_version: str) -> ConnectorUnderTest:
    return await ConnectorUnderTest.from_image_name(dagger_client, f"{connector_image}:{target_version}", TargetOrControl.TARGET)


@pytest.fixture(scope="session")
def duckdb_path(request: SubRequest) -> Path:
    return request.config.stash[stash_keys.DUCKDB_PATH]


@pytest.fixture(scope="session")
def spec_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    actor_id: str,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        actor_id=actor_id,
        command=Command.SPEC,
        global_output_dir=test_artifacts_directory,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
def spec_control_connector_runner(
    dagger_client: dagger.Client,
    spec_control_execution_inputs: ExecutionInputs,
) -> ConnectorRunner:
    runner = ConnectorRunner(
        dagger_client,
        spec_control_execution_inputs,
    )
    return runner


@pytest.fixture(scope="session")
async def spec_control_execution_result(
    request: SubRequest,
    spec_control_execution_inputs: ExecutionInputs,
    spec_control_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running spec for control connector {spec_control_execution_inputs.connector_under_test.name}")
    execution_result = await spec_control_connector_runner.run()
    request.config.stash[stash_keys.REPORT].add_control_execution_result(execution_result)
    return execution_result


@pytest.fixture(scope="session")
def spec_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    actor_id: str,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.SPEC,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
def spec_target_connector_runner(
    dagger_client: dagger.Client,
    spec_target_execution_inputs: ExecutionInputs,
) -> ConnectorRunner:
    runner = ConnectorRunner(
        dagger_client,
        spec_target_execution_inputs,
    )
    return runner


@pytest.fixture(scope="session")
async def spec_target_execution_result(
    request: SubRequest,
    spec_target_execution_inputs: ExecutionInputs,
    spec_target_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running spec for target connector {spec_target_execution_inputs.connector_under_test.name}")
    execution_result = await spec_target_connector_runner.run()

    request.config.stash[stash_keys.REPORT].add_target_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
def check_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.CHECK,
        config=connector_config,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
async def check_control_connector_runner(
    dagger_client: dagger.Client,
    check_control_execution_inputs: ExecutionInputs,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(dagger_client, "proxy_server_check_control", connection_id)

    runner = ConnectorRunner(
        dagger_client,
        check_control_execution_inputs,
        http_proxy=proxy,
    )
    yield runner
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def check_control_execution_result(
    request: SubRequest,
    check_control_execution_inputs: ExecutionInputs,
    check_control_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running check for control connector {check_control_execution_inputs.connector_under_test.name}")
    execution_result = await check_control_connector_runner.run()

    request.config.stash[stash_keys.REPORT].add_control_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
def check_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.CHECK,
        config=connector_config,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
async def check_target_connector_runner(
    check_control_execution_result: ExecutionResult,
    dagger_client: dagger.Client,
    check_target_execution_inputs: ExecutionInputs,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(
        dagger_client,
        "proxy_server_check_target",
        connection_id,
        stream_for_server_replay=check_control_execution_result.http_dump,
    )
    runner = ConnectorRunner(
        dagger_client,
        check_target_execution_inputs,
        http_proxy=proxy,
    )
    yield runner
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def check_target_execution_result(
    request: SubRequest,
    test_artifacts_directory: Path,
    check_target_execution_inputs: ExecutionInputs,
    check_target_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running check for target connector {check_target_execution_inputs.connector_under_test.name}")
    execution_result = await check_target_connector_runner.run()
    request.config.stash[stash_keys.REPORT].add_target_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
def discover_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.DISCOVER,
        config=connector_config,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
async def discover_control_execution_result(
    request: SubRequest,
    discover_control_execution_inputs: ExecutionInputs,
    discover_control_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running discover for control connector {discover_control_execution_inputs.connector_under_test.name}")
    execution_result = await discover_control_connector_runner.run()
    request.config.stash[stash_keys.REPORT].add_control_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
def discover_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.DISCOVER,
        config=connector_config,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
async def discover_control_connector_runner(
    dagger_client: dagger.Client,
    discover_control_execution_inputs: ExecutionInputs,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(dagger_client, "proxy_server_discover_control", connection_id)

    yield ConnectorRunner(
        dagger_client,
        discover_control_execution_inputs,
        http_proxy=proxy,
    )
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def discover_target_connector_runner(
    dagger_client: dagger.Client,
    discover_control_execution_result: ExecutionResult,
    discover_target_execution_inputs: ExecutionInputs,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(
        dagger_client,
        "proxy_server_discover_target",
        connection_id,
        stream_for_server_replay=discover_control_execution_result.http_dump,
    )

    yield ConnectorRunner(
        dagger_client,
        discover_target_execution_inputs,
        http_proxy=proxy,
    )
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def discover_target_execution_result(
    request: SubRequest,
    discover_target_execution_inputs: ExecutionInputs,
    discover_target_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running discover for target connector {discover_target_execution_inputs.connector_under_test.name}")
    execution_result = await discover_target_connector_runner.run()
    request.config.stash[stash_keys.REPORT].add_target_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
def read_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    configured_catalog: ConfiguredAirbyteCatalog,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=control_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.READ,
        configured_catalog=configured_catalog,
        config=connector_config,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
def read_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    configured_catalog: ConfiguredAirbyteCatalog,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    return ExecutionInputs(
        connector_under_test=target_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.READ,
        configured_catalog=configured_catalog,
        config=connector_config,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
async def read_control_connector_runner(
    dagger_client: dagger.Client,
    read_control_execution_inputs: ExecutionInputs,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(dagger_client, "proxy_server_read_control", connection_id)

    yield ConnectorRunner(
        dagger_client,
        read_control_execution_inputs,
        http_proxy=proxy,
    )
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def read_control_execution_result(
    request: SubRequest,
    read_control_execution_inputs: ExecutionInputs,
    read_control_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running read for control connector {read_control_execution_inputs.connector_under_test.name}")
    execution_result = await read_control_connector_runner.run()

    request.config.stash[stash_keys.REPORT].add_control_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
async def read_target_connector_runner(
    dagger_client: dagger.Client,
    read_target_execution_inputs: ExecutionInputs,
    read_control_execution_result: ExecutionResult,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(
        dagger_client,
        "proxy_server_read_target",
        connection_id,
        stream_for_server_replay=read_control_execution_result.http_dump,
    )

    yield ConnectorRunner(
        dagger_client,
        read_target_execution_inputs,
        http_proxy=proxy,
    )
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def read_target_execution_result(
    request: SubRequest,
    record_testsuite_property: Callable,
    read_target_execution_inputs: ExecutionInputs,
    read_target_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    logging.info(f"Running read for target connector {read_target_execution_inputs.connector_under_test.name}")
    execution_result = await read_target_connector_runner.run()

    request.config.stash[stash_keys.REPORT].add_target_execution_result(execution_result)
    return execution_result


@pytest.fixture(scope="session")
def read_with_state_control_execution_inputs(
    control_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    configured_catalog: ConfiguredAirbyteCatalog,
    state: dict,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    if not state:
        pytest.skip("The state is not provided. Skipping the test as it's not possible to run a read with state.")
    return ExecutionInputs(
        connector_under_test=control_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.READ_WITH_STATE,
        configured_catalog=configured_catalog,
        config=connector_config,
        state=state,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
def read_with_state_target_execution_inputs(
    target_connector: ConnectorUnderTest,
    actor_id: str,
    connector_config: SecretDict,
    configured_catalog: ConfiguredAirbyteCatalog,
    state: dict,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    if not state:
        pytest.skip("The state is not provided. Skipping the test as it's not possible to run a read with state.")
    return ExecutionInputs(
        connector_under_test=target_connector,
        actor_id=actor_id,
        global_output_dir=test_artifacts_directory,
        command=Command.READ_WITH_STATE,
        configured_catalog=configured_catalog,
        config=connector_config,
        state=state,
        duckdb_path=duckdb_path,
    )


@pytest.fixture(scope="session")
async def read_with_state_control_connector_runner(
    dagger_client: dagger.Client,
    read_with_state_control_execution_inputs: ExecutionInputs,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(dagger_client, "proxy_server_read_with_state_control", connection_id)

    yield ConnectorRunner(
        dagger_client,
        read_with_state_control_execution_inputs,
        http_proxy=proxy,
    )
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def read_with_state_control_execution_result(
    request: SubRequest,
    read_with_state_control_execution_inputs: ExecutionInputs,
    read_with_state_control_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    if read_with_state_control_execution_inputs.state is None:
        pytest.skip("The control state is not provided. Skipping the test as it's not possible to run a read with state.")

    logging.info(f"Running read with state for control connector {read_with_state_control_execution_inputs.connector_under_test.name}")
    execution_result = await read_with_state_control_connector_runner.run()
    request.config.stash[stash_keys.REPORT].add_control_execution_result(execution_result)

    return execution_result


@pytest.fixture(scope="session")
async def read_with_state_target_connector_runner(
    dagger_client: dagger.Client,
    read_with_state_target_execution_inputs: ExecutionInputs,
    read_with_state_control_execution_result: ExecutionResult,
    connection_id: str,
) -> AsyncGenerator:
    proxy = Proxy(
        dagger_client,
        "proxy_server_read_with_state_target",
        connection_id,
        stream_for_server_replay=read_with_state_control_execution_result.http_dump,
    )
    yield ConnectorRunner(
        dagger_client,
        read_with_state_target_execution_inputs,
        http_proxy=proxy,
    )
    await proxy.clear_cache_volume()


@pytest.fixture(scope="session")
async def read_with_state_target_execution_result(
    request: SubRequest,
    read_with_state_target_execution_inputs: ExecutionInputs,
    read_with_state_target_connector_runner: ConnectorRunner,
) -> ExecutionResult:
    if read_with_state_target_execution_inputs.state is None:
        pytest.skip("The target state is not provided. Skipping the test as it's not possible to run a read with state.")
    logging.info(f"Running read with state for target connector {read_with_state_target_execution_inputs.connector_under_test.name}")
    execution_result = await read_with_state_target_connector_runner.run()
    request.config.stash[stash_keys.REPORT].add_target_execution_result(execution_result)

    return execution_result
