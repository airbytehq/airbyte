#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from ci_connector_ops.pipelines.actions.build_contexts import PYPROJECT_TOML_FILE_PATH
from ci_connector_ops.pipelines.utils import StepStatus, check_path_in_workdir
from ci_connector_ops.utils import Connector
from dagger.api.gen import Client, Container

RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "--check", "."]
RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{PYPROJECT_TOML_FILE_PATH}", "."]


async def _run_tests_in_directory(connector_container: Container, test_directory: str) -> StepStatus:
    """Runs the pytest tests in the test_directory that was passed.
    A StepStatus.SKIPPED is returned if no tests were discovered.
    Args:
        connector_container (Container): A connector containers with test dependencies installed.
        test_directory (str): The directory in which the tests are declared.

    Returns:
        StepStatus: Failure or success status of the tests.
    """
    # Question to dagger team: according to https://github.com/dagger/dagger/issues/3192 :
    # A with_exec returning a non 0 status code will throw a TransportQueryError
    # How can we execute with_exec commands that may return non 0 status code and decide further in the pipeline how to handle these status code
    # If I'm not mistaken these TransportQueryError will stop the global pipeline execution
    # In other words, if this with_exec fails we can't run other tests and get their results.
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
    """Run a code format check on the container source code.
    We call black, isort and flake commands:
    - Black formats the code: fails if the code is not formatted.
    - Isort checks the import orders: fails if the import are not properly ordered.
    - Flake enforces style-guides: fails if the style-guide is not followed.
    Args:
        connector_container (Container): _description_

    Returns:
        StepStatus: Failure or success status of the check.
    """
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
    """Run all pytest tests declared in the unit_tests directory of the connector code.

    Args:
        connector_container (Container): A connector containers with test dependencies installed.

    Returns:
        StepStatus: Failure, skip or success status of the unit tests run.
    """
    return await _run_tests_in_directory(connector_container, "unit_tests")


async def run_integration_tests(connector_container: Container) -> StepStatus:
    """Run all pytest tests declared in the integration_tests directory of the connector code.

    Args:
        connector_container (Container): A connector containers with test dependencies installed.

    Returns:
        StepStatus: Failure, skip or success status of the integration tests run.
    """
    return await _run_tests_in_directory(connector_container, "integration_tests")


async def run_acceptance_tests(
    dagger_client: Client,
    connector: Connector,
    connector_under_test_image_id: str,
    connector_acceptance_test_image: str = "airbyte/connector-acceptance-test:latest",
) -> StepStatus:
    """Run the connector-acceptance-test on a connector.
    1. Build connector-acceptance-test if the input image tag finishes by :dev, otherwise an already built image
    2. Read connector secrets from GSM and write them locally in the connector code directory
    3. Run connector-acceptance-test image with mounted connector code directory under /test_input

    NB: We pass the connector under test image id to use its value as a cache buster.

    Args:
        dagger_client (Client): The dagger client to use.
        connector (Connector): The connector under test.
        connector_under_test_image_id (str): The connector under test image id, used as a cache buster for connector-acceptance-test execution.
        connector_acceptance_test_image (str, optional): The connector-acceptance-test image name. Defaults to "airbyte/connector-acceptance-test:latest".

    Returns:
        StepStatus: Failure or success status of the acceptance tests run.
    """

    # Question to Dagger team:
    # To make this execution work as expected I had to patch our connector-acceptance-test code to not rely on volume binding to mount connector configurations to the connector under test.
    # I replaced bind mounts with temporary image build of the connector under test in connector-acceptance-test.
    # In this temporary image's dockerfile has COPY instructions to make connector configurations available in the connector under tests  (which is my workaround to volume mounts).
    # If we use the latest connector_acceptance_test_image (which holds our unpatched logic) the connector under tests can't find the files we mount to it with bindings.
    # This is because, with bindings, the connector under test looks for configurations on the host disk.
    # But this configurations does not exists because they are created at runtime by the connector-acceptance-test
    # I can't use exports because the configuration generation and the tests are launched in the same with_exec instructions.
    # I can't easily decouple configuration generation and tests execution because all this logic is dynamically generated by pytest and its test discovery / fixture management.
    # I'd love to find a workaround that would allow me to not patch connector-acceptance-test.
    # This was already extensively discussed here with no workaround found ATM: https://discord.com/channels/707636530424053791/1078038429163597854
    # The critical code path on connector-acceptance-test is here: https://github.com/airbytehq/airbyte/blob/fbd6dbf091e5605b140971ef049a261c59ff1f9a/airbyte-integrations/bases/connector-acceptance-test/connector_acceptance_test/utils/connector_runner.py#L104
    source_host_path = dagger_client.host().directory(str(connector.code_directory))
    docker_host_socket = dagger_client.host().unix_socket("/var/run/docker.sock")

    if not connector.acceptance_test_config:
        return StepStatus.SKIPPED

    if connector_acceptance_test_image.endswith(":dev"):
        cat_container = dagger_client.host().directory("airbyte-integrations/bases/connector-acceptance-test").docker_build()
    else:
        cat_container = dagger_client.container().from_(connector_acceptance_test_image)

    cat_container = (
        cat_container.with_unix_socket("/var/run/docker.sock", docker_host_socket)
        .with_workdir("/test_input")
        .with_env_variable("CACHEBUSTER", connector_under_test_image_id)
        .with_mounted_directory("/test_input", source_host_path)
        .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "-r", "fEsx"])
        .with_exec(["--acceptance-test-config", "/test_input"])
    )

    return StepStatus.from_exit_code(await cat_container.exit_code())
