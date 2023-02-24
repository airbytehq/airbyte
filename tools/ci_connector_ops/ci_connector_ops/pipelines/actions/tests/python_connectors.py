#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.ci.actions.build_contexts.python_connectors import PYPROJECT_TOML_FILE_PATH
from ci_connector_ops.ci.utils import check_path_in_workdir
from dagger.api.gen import Container

RUN_BLACK_CMD = ["python", "-m", "black", "--config=/pyproject.toml", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", "--settings-file=/pyproject.toml", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", "--config=/pyproject.toml", "."]


async def check_format(connector_container: Container):
    formatter = (
        connector_container.Pipeline("Format Check")
        .with_exec(["echo", "Running black"])
        .with_exec(RUN_BLACK_CMD)
        .with_exec(["echo", "Running Isort"])
        .with_exec(RUN_ISORT_CMD)
        .with_exec(["echo", "Running Flake"])
        .with_exec(RUN_FLAKE_CMD)
    )
    return await formatter.exit_code()


async def _run_tests_in_directory(connector_container: Container, test_directory: str):
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
        return await tester.exit_code()
    else:
        return 0


async def run_unit_tests(connector_container: Container):
    return await _run_tests_in_directory(connector_container.Pipeline("unit_tests"), "unit_tests")


async def run_integration_tests(connector_container: Container):
    return await _run_tests_in_directory(connector_container.Pipeline("integration_tests"), "integration_tests")


# async def run_acceptance_tests(client, connector_name):
#     source_host_path = client.host().directory(f"airbyte-integrations/connectors/{connector_name}")

#     docker_host_socket = client.host().unix_socket("/var/run/docker.sock")

#     if Path(f"airbyte-integrations/connectors/{connector_name}/acceptance-test-config.yml").is_file():
#         cat_container = (
#             client.host()
#             .directory("airbyte-integrations/bases/connector-acceptance-test")
#             .docker_build()
#             .with_unix_socket("/var/run/docker.sock", docker_host_socket)
#             .with_workdir("/test_input")
#             .with_mounted_directory("/test_input", source_host_path)
#             .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"])
#             .with_env_variable("CACHEBUSTER", datetime.datetime.now().isoformat())
#             .with_exec(["--acceptance-test-config", "/test_input"])
#         )

#         return await cat_container.exit_code()
