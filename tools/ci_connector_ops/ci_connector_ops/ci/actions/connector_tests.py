#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from pathlib import Path

from ci_connector_ops.ci.actions.connector_builder import PYPROJECT_TOML_FILE_PATH, connector_has_path

RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "."]


async def _run_tests_in_directory(connector_builder, test_directory):
    test_config = "pytest.ini" if await connector_has_path(connector_builder, "pytest.ini") else "/" + PYPROJECT_TOML_FILE_PATH
    if await connector_has_path(connector_builder, test_directory):
        tester = connector_builder.with_exec(
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
        return await tester.exit_code()
    else:
        return 0


async def unit_tests(connector_builder):
    return await _run_tests_in_directory(connector_builder, "unit_tests")


async def integration_tests(connector_builder):
    return await _run_tests_in_directory(connector_builder, "integration_tests")


async def acceptance_tests(client, connector_name):
    source_host_path = client.host().directory(f"airbyte-integrations/connectors/{connector_name}")

    docker_host_socket = client.host().unix_socket("/var/run/docker.sock")

    if Path(f"airbyte-integrations/connectors/{connector_name}/acceptance-test-config.yml").is_file():
        cat_container = (
            client.host()
            .directory("airbyte-integrations/bases/connector-acceptance-test")
            .docker_build()
            .with_unix_socket("/var/run/docker.sock", docker_host_socket)
            .with_workdir("/test_input")
            .with_mounted_directory("/test_input", source_host_path)
            .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"])
            .with_env_variable("CACHEBUSTER", datetime.datetime.now().isoformat())
            .with_exec(["--acceptance-test-config", "/test_input"])
        )

        return await cat_container.exit_code()
        # return await (
        #     client.host()
        #     .directory("airbyte-integrations/bases/connector-acceptance-test")
        #     .docker_build()
        #     .with_unix_socket("/var/run/docker.sock", docker_host_socket)
        #     .with_workdir("/test_input")
        #     .with_mounted_directory("/test_input", source_host_path)
        #     .with_entrypoint(["python", "-m", "pytest", "--basetemp=/tmp/toto", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"])
        #     .with_exec(["--acceptance-test-config", "/test_input"])
        #     .stdout()
        # )

    # return await (
    #     cat_container
    #     .with_mounted_directory("/test_input", source_host_path)
    #     .with_mounted_directory("/tmp", client.host().directory("/tmp"))
    #     .with_exec(["--acceptance-test-config", "/test_input"])
    #     .exit_code()
    # )
