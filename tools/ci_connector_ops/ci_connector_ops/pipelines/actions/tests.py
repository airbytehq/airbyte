#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from ci_connector_ops.pipelines.actions.build_contexts import PYPROJECT_TOML_FILE_PATH
from ci_connector_ops.pipelines.utils import StepStatus, check_path_in_workdir
from ci_connector_ops.utils import Connector
from dagger.api.gen import Container

RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "."]


async def _run_tests_in_directory(connector_container: Container, test_directory: str) -> int:
    test_config = "pytest.ini" if await check_path_in_workdir(connector_container, "pytest.ini") else "/" + PYPROJECT_TOML_FILE_PATH
    if await check_path_in_workdir(connector_container, test_directory):
        tester = connector_container.with_exec(
            [
                "python",
                "-m",
                "pytest",
                "--suppress-no-test-exit-code",  # This is a patch until https://github.com/dagger/dagger/issues/3192 is fixed
                "-s",
                test_directory,
                "-c",
                test_config,
            ]
        )
        return StepStatus.from_exit_code(await tester.exit_code())
    else:
        return StepStatus.SKIPPED


async def check_format(connector_container: Container) -> StepStatus:
    formatter = (
        connector_container.with_exec(["echo", "Running black"])
        .with_exec(RUN_BLACK_CMD)
        .with_exec(["echo", "Running Isort"])
        .with_exec(RUN_ISORT_CMD)
        .with_exec(["echo", "Running Flake"])
        .with_exec(RUN_FLAKE_CMD)
    )
    return StepStatus.from_exit_code(await formatter.exit_code())


async def run_unit_tests(connector_container: Container) -> StepStatus:
    return await _run_tests_in_directory(connector_container, "unit_tests")


async def run_integration_tests(connector_container: Container) -> StepStatus:
    return await _run_tests_in_directory(connector_container, "integration_tests")


async def run_acceptance_tests(client, connector: Connector, connector_acceptance_test_version: str = "latest") -> StepStatus:
    source_host_path = client.host().directory(str(connector.code_directory))
    docker_host_socket = client.host().unix_socket("/var/run/docker.sock")

    if not connector.acceptance_test_config:
        return StepStatus.SKIPPED

    if connector_acceptance_test_version == "dev":
        cat_container = client.host().directory("airbyte-integrations/bases/connector-acceptance-test").docker_build()
    else:
        cat_container = client.container().from_(f"airbyte/connector-acceptance-test:{connector_acceptance_test_version}")

    cat_container = (
        cat_container.with_unix_socket("/var/run/docker.sock", docker_host_socket)
        .with_workdir("/test_input")
        .with_mounted_directory("/test_input", source_host_path)
        .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"])
        .with_exec(["--acceptance-test-config", "/test_input"])
    )

    return StepStatus.from_exit_code(await cat_container.exit_code())
