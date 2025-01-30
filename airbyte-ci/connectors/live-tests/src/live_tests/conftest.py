# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import hashlib
import logging
import os
import textwrap
import time
import webbrowser
from collections.abc import AsyncGenerator, AsyncIterable, Callable, Generator, Iterable
from itertools import product
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import dagger
import pytest
from airbyte_protocol.models import AirbyteCatalog, AirbyteStateMessage, ConfiguredAirbyteCatalog, ConnectorSpecification  # type: ignore
from connection_retriever.audit_logging import get_user_email  # type: ignore
from connection_retriever.retrieval import ConnectionNotFoundError, get_current_docker_image_tag  # type: ignore
from rich.prompt import Confirm, Prompt

from live_tests import stash_keys
from live_tests.commons.connection_objects_retrieval import ConnectionObject, InvalidConnectionError, get_connection_objects
from live_tests.commons.connector_runner import ConnectorRunner, Proxy
from live_tests.commons.evaluation_modes import TestEvaluationMode
from live_tests.commons.models import (
    ActorType,
    Command,
    ConnectionObjects,
    ConnectionSubset,
    ConnectorUnderTest,
    ExecutionInputs,
    ExecutionResult,
    SecretDict,
    TargetOrControl,
)
from live_tests.commons.secret_access import get_airbyte_api_key
from live_tests.commons.segment_tracking import track_usage
from live_tests.commons.utils import clean_up_artifacts
from live_tests.report import PrivateDetailsReport, ReportState, TestReport
from live_tests.utils import get_catalog, get_spec

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser
    from _pytest.fixtures import SubRequest
    from pytest_sugar import SugarTerminalReporter  # type: ignore

# CONSTS
LOGGER = logging.getLogger("live-tests")
MAIN_OUTPUT_DIRECTORY = Path("/tmp/live_tests_artifacts")

# It's used by Dagger and its very verbose
logging.getLogger("httpx").setLevel(logging.ERROR)


# PYTEST HOOKS
def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--connector-image",
        help="The connector image name on which the tests will run: e.g. airbyte/source-faker",
    )
    parser.addoption(
        "--control-version",
        help="The control version used for regression testing.",
    )
    parser.addoption(
        "--target-version",
        default="dev",
        help="The target version used for regression and validation testing. Defaults to dev.",
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
    parser.addoption(
        "--test-evaluation-mode",
        choices=[e.value for e in TestEvaluationMode],
        default=TestEvaluationMode.STRICT.value,
        help='If "diagnostic" mode is selected, all tests will pass as long as there is no exception; warnings will be logged. In "strict" mode, tests may fail.',
    )
    parser.addoption(
        "--connection-subset",
        choices=[c.value for c in ConnectionSubset],
        default=ConnectionSubset.SANDBOXES.value,
        help="Whether to select from sandbox accounts only.",
    )
    parser.addoption(
        "--max-connections",
        default=None,
        help="The maximum number of connections to retrieve and use for testing.",
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
    private_details_path = test_artifacts_directory / "private_details.html"
    config.stash[stash_keys.TEST_ARTIFACT_DIRECTORY] = test_artifacts_directory
    dagger_log_path.touch()
    LOGGER.info("Dagger log path: %s", dagger_log_path)
    config.stash[stash_keys.DAGGER_LOG_PATH] = dagger_log_path
    config.stash[stash_keys.PR_URL] = get_option_or_fail(config, "--pr-url")
    _connection_id = config.getoption("--connection-id")
    config.stash[stash_keys.AUTO_SELECT_CONNECTION] = _connection_id == "auto"
    config.stash[stash_keys.CONNECTOR_IMAGE] = get_option_or_fail(config, "--connector-image")
    config.stash[stash_keys.TARGET_VERSION] = get_option_or_fail(config, "--target-version")
    config.stash[stash_keys.CONTROL_VERSION] = get_control_version(config)
    config.stash[stash_keys.CONNECTION_SUBSET] = ConnectionSubset(get_option_or_fail(config, "--connection-subset"))
    custom_source_config_path = config.getoption("--config-path")
    custom_configured_catalog_path = config.getoption("--catalog-path")
    custom_state_path = config.getoption("--state-path")
    config.stash[stash_keys.SELECTED_STREAMS] = set(config.getoption("--stream") or [])
    config.stash[stash_keys.TEST_EVALUATION_MODE] = TestEvaluationMode(config.getoption("--test-evaluation-mode", "strict"))
    config.stash[stash_keys.MAX_CONNECTIONS] = config.getoption("--max-connections")
    config.stash[stash_keys.MAX_CONNECTIONS] = (
        int(config.stash[stash_keys.MAX_CONNECTIONS]) if config.stash[stash_keys.MAX_CONNECTIONS] else None
    )

    if config.stash[stash_keys.RUN_IN_AIRBYTE_CI]:
        config.stash[stash_keys.SHOULD_READ_WITH_STATE] = bool(config.getoption("--should-read-with-state"))
    elif _should_read_with_state := config.getoption("--should-read-with-state"):
        config.stash[stash_keys.SHOULD_READ_WITH_STATE] = _should_read_with_state
    else:
        config.stash[stash_keys.SHOULD_READ_WITH_STATE] = prompt_for_read_with_or_without_state()

    retrieval_reason = f"Running live tests on connection for connector {config.stash[stash_keys.CONNECTOR_IMAGE]} on target versions ({config.stash[stash_keys.TARGET_VERSION]})."

    try:
        config.stash[stash_keys.ALL_CONNECTION_OBJECTS] = get_connection_objects(
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
            connector_image=config.stash[stash_keys.CONNECTOR_IMAGE],
            connector_version=config.stash[stash_keys.CONTROL_VERSION],
            auto_select_connections=config.stash[stash_keys.AUTO_SELECT_CONNECTION],
            selected_streams=config.stash[stash_keys.SELECTED_STREAMS],
            connection_subset=config.stash[stash_keys.CONNECTION_SUBSET],
            max_connections=config.stash[stash_keys.MAX_CONNECTIONS],
        )
        config.stash[stash_keys.IS_PERMITTED_BOOL] = True
    except (ConnectionNotFoundError, InvalidConnectionError) as exc:
        clean_up_artifacts(MAIN_OUTPUT_DIRECTORY, LOGGER)
        LOGGER.error(
            f"Failed to retrieve a valid a connection which is using the control version {config.stash[stash_keys.CONTROL_VERSION]}."
        )
        pytest.exit(str(exc))

    if config.stash[stash_keys.CONTROL_VERSION] == config.stash[stash_keys.TARGET_VERSION]:
        pytest.exit(f"Control and target versions are the same: {control_version}. Please provide different versions.")

    config.stash[stash_keys.PRIVATE_DETAILS_REPORT] = PrivateDetailsReport(
        private_details_path,
        config,
    )

    config.stash[stash_keys.TEST_REPORT] = TestReport(
        report_path,
        config,
        private_details_url=config.stash[stash_keys.PRIVATE_DETAILS_REPORT].path.resolve().as_uri(),
    )

    webbrowser.open_new_tab(config.stash[stash_keys.TEST_REPORT].path.resolve().as_uri())


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
    config.stash[stash_keys.TEST_REPORT].update(ReportState.FINISHED)
    config.stash[stash_keys.PRIVATE_DETAILS_REPORT].update(ReportState.FINISHED)
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

    # Overwrite test failures with passes for tests being run in diagnostic mode
    if (
        item.config.stash.get(stash_keys.TEST_EVALUATION_MODE, TestEvaluationMode.STRICT) == TestEvaluationMode.DIAGNOSTIC
        and "allow_diagnostic_mode" in item.keywords
    ):
        if call.when == "call":
            if call.excinfo:
                if report.outcome == "failed":
                    report.outcome = "passed"

    # This is to add skipped or failed tests due to upstream fixture failures on setup
    if report.outcome in ["failed", "skipped"] or report.when == "call":
        item.config.stash[stash_keys.TEST_REPORT].add_test_result(
            report,
            item.function.__doc__,  # type: ignore
        )


# HELPERS


def get_option_or_fail(config: pytest.Config, option: str) -> str:
    if option_value := config.getoption(option):
        return option_value
    pytest.fail(f"Missing required option: {option}")


def get_control_version(config: pytest.Config) -> str:
    if control_version := config.getoption("--control-version"):
        return control_version
    if connector_docker_repository := config.getoption("--connector-image"):
        return get_current_docker_image_tag(connector_docker_repository)
    raise ValueError("The control version can't be determined, please pass a --control-version or a --connector-image")


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


# FIXTURES


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
def all_connection_objects(request: SubRequest) -> List[ConnectionObjects]:
    return request.config.stash[stash_keys.ALL_CONNECTION_OBJECTS]


def get_connector_config(connection_objects: ConnectionObjects, control_connector: ConnectorUnderTest) -> Optional[SecretDict]:
    if control_connector.actor_type is ActorType.SOURCE:
        return connection_objects.source_config
    elif control_connector.actor_type is ActorType.DESTINATION:
        return connection_objects.destination_config
    else:
        raise ValueError(f"Actor type {control_connector.actor_type} is not supported")


@pytest.fixture(scope="session")
def actor_id(connection_objects: ConnectionObjects, control_connector: ConnectorUnderTest) -> str | None:
    if control_connector.actor_type is ActorType.SOURCE:
        return connection_objects.source_id
    elif control_connector.actor_type is ActorType.DESTINATION:
        return connection_objects.destination_id
    else:
        raise ValueError(f"Actor type {control_connector.actor_type} is not supported")


def get_actor_id(connection_objects: ConnectionObjects, control_connector: ConnectorUnderTest) -> str | None:
    if control_connector.actor_type is ActorType.SOURCE:
        return connection_objects.source_id
    elif control_connector.actor_type is ActorType.DESTINATION:
        return connection_objects.destination_id
    else:
        raise ValueError(f"Actor type {control_connector.actor_type} is not supported")


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


def get_execution_inputs_for_command(
    command: Command,
    connection_objects: ConnectionObjects,
    control_connector: ConnectorUnderTest,
    test_artifacts_directory: Path,
    duckdb_path: Path,
) -> ExecutionInputs:
    """Get the execution inputs for the given command and connection objects."""
    actor_id = get_actor_id(connection_objects, control_connector)

    inputs_arguments = {
        "hashed_connection_id": connection_objects.hashed_connection_id,
        "connector_under_test": control_connector,
        "actor_id": actor_id,
        "global_output_dir": test_artifacts_directory,
        "command": command,
        "duckdb_path": duckdb_path,
    }

    if command.needs_config:
        connector_config = get_connector_config(connection_objects, control_connector)
        if not connector_config:
            pytest.skip("Config is not provided. The config fixture can't be used.")
        inputs_arguments["config"] = connector_config
    if command.needs_catalog:
        configured_catalog = connection_objects.configured_catalog
        if not configured_catalog:
            pytest.skip("Catalog is not provided. The catalog fixture can't be used.")
        inputs_arguments["configured_catalog"] = connection_objects.configured_catalog
    if command.needs_state:
        state = connection_objects.state
        if not state:
            pytest.skip("State is not provided. The state fixture can't be used.")
        inputs_arguments["state"] = state

    return ExecutionInputs(**inputs_arguments)


async def run_command(
    dagger_client: dagger.Client,
    command: Command,
    connection_objects: ConnectionObjects,
    connector: ConnectorUnderTest,
    test_artifacts_directory: Path,
    duckdb_path: Path,
    runs_in_ci,
    enable_proxy: bool = True,
) -> ExecutionResult:
    """Run the given command for the given connector and connection objects."""
    execution_inputs = get_execution_inputs_for_command(command, connection_objects, connector, test_artifacts_directory, duckdb_path)
    logging.info(f"Running {command} for {connector.target_or_control.value} connector {execution_inputs.connector_under_test.name}")
    proxy_hostname = f"proxy_server_{command.value}_{execution_inputs.connector_under_test.version.replace('.', '_')}"
    proxy = Proxy(dagger_client, proxy_hostname, connection_objects.connection_id)
    kwargs = {}
    if enable_proxy:
        kwargs["http_proxy"] = proxy
    runner = ConnectorRunner(
        dagger_client,
        execution_inputs,
        runs_in_ci,
        **kwargs
    )
    execution_result = await runner.run()
    return execution_result, proxy


async def run_command_and_add_to_report(
    dagger_client: dagger.Client,
    command: Command,
    connection_objects: ConnectionObjects,
    connector: ConnectorUnderTest,
    test_artifacts_directory: Path,
    duckdb_path: Path,
    runs_in_ci,
    test_report: TestReport,
    private_details_report: PrivateDetailsReport,
    enable_proxy: bool = True,
) -> ExecutionResult:
    """Run the given command for the given connector and connection objects and add the results to the test report."""
    execution_result, proxy = await run_command(
        dagger_client,
        command,
        connection_objects,
        connector,
        test_artifacts_directory,
        duckdb_path,
        runs_in_ci,
        enable_proxy=enable_proxy,
    )
    if connector.target_or_control is TargetOrControl.CONTROL:
        test_report.add_control_execution_result(execution_result)
        private_details_report.add_control_execution_result(execution_result)
    if connector.target_or_control is TargetOrControl.TARGET:
        test_report.add_target_execution_result(execution_result)
        private_details_report.add_target_execution_result(execution_result)
    return execution_result, proxy


def generate_execution_results_fixture(command: Command, control_or_target: str) -> Callable:
    """Dynamically generate the fixture for the given command and control/target.
    This is mainly to avoid code duplication and to make the code more maintainable.
    Declaring this explicitly for each command and control/target combination would be cumbersome.
    """

    if control_or_target not in ["control", "target"]:
        raise ValueError("control_or_target should be either 'control' or 'target'")
    if command not in [Command.SPEC, Command.CHECK, Command.DISCOVER, Command.READ, Command.READ_WITH_STATE]:
        raise ValueError("command should be either 'spec', 'check', 'discover', 'read' or 'read_with_state'")

    if control_or_target == "control":

        @pytest.fixture(scope="session")
        async def generated_fixture(
            request: SubRequest, dagger_client: dagger.Client, control_connector: ConnectorUnderTest, test_artifacts_directory: Path
        ) -> ExecutionResult:
            connection_objects = request.param

            execution_results, proxy = await run_command_and_add_to_report(
                dagger_client,
                command,
                connection_objects,
                control_connector,
                test_artifacts_directory,
                request.config.stash[stash_keys.DUCKDB_PATH],
                request.config.stash[stash_keys.RUN_IN_AIRBYTE_CI],
                request.config.stash[stash_keys.TEST_REPORT],
                request.config.stash[stash_keys.PRIVATE_DETAILS_REPORT],
            )

            yield execution_results
            await proxy.clear_cache_volume()

    else:

        @pytest.fixture(scope="session")
        async def generated_fixture(
            request: SubRequest, dagger_client: dagger.Client, target_connector: ConnectorUnderTest, test_artifacts_directory: Path
        ) -> ExecutionResult:
            connection_objects = request.param

            execution_results, proxy = await run_command_and_add_to_report(
                dagger_client,
                command,
                connection_objects,
                target_connector,
                test_artifacts_directory,
                request.config.stash[stash_keys.DUCKDB_PATH],
                request.config.stash[stash_keys.RUN_IN_AIRBYTE_CI],
                request.config.stash[stash_keys.TEST_REPORT],
                request.config.stash[stash_keys.PRIVATE_DETAILS_REPORT],
            )

            yield execution_results
            await proxy.clear_cache_volume()

    return generated_fixture


def inject_fixtures() -> set[str]:
    """Dynamically generate th execution result fixtures for all the combinations of commands and control/target.
    The fixtures will be named as <command>_<control/target>_execution_result
    Add the generated fixtures to the global namespace.
    """
    execution_result_fixture_names = []
    for command, control_or_target in product([command for command in Command], ["control", "target"]):
        fixture_name = f"{command.name.lower()}_{control_or_target}_execution_result"
        globals()[fixture_name] = generate_execution_results_fixture(command, control_or_target)
        execution_result_fixture_names.append(fixture_name)
    return set(execution_result_fixture_names)


EXECUTION_RESULT_FIXTURES = inject_fixtures()


def pytest_generate_tests(metafunc):
    """This function is called for each test function.
    It helps in parameterizing the test functions with the connection objects.
    It will provide the connection objects to the "*_execution_result" fixtures as parameters.
    This will make sure that the tests are run for all the connection objects available in the configuration.
    """
    all_connection_objects = metafunc.config.stash[stash_keys.ALL_CONNECTION_OBJECTS]
    requested_fixtures = [fixture_name for fixture_name in metafunc.fixturenames if fixture_name in EXECUTION_RESULT_FIXTURES]
    assert isinstance(all_connection_objects, list), "all_connection_objects should be a list"

    if not requested_fixtures:
        return
    metafunc.parametrize(
        requested_fixtures,
        [[c] * len(requested_fixtures) for c in all_connection_objects],
        indirect=requested_fixtures,
        ids=[f"CONNECTION {hashlib.sha256(c.connection_id.encode()).hexdigest()[:7]}" for c in all_connection_objects],
    )
