#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests for a specific connector given a test context."""

import json
import uuid
from abc import ABC
from typing import List, Tuple

import asyncer
from ci_connector_ops.pipelines.actions import environments, secrets
from ci_connector_ops.pipelines.bases import Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.pipelines.utils import check_path_in_workdir
from dagger import CacheSharingMode, Container


class ConnectorInstallTest(Step):
    title = "Connector package install"

    async def _run(self) -> Tuple[StepResult, Container]:
        """Install the connector under test package in a Python container.

        Returns:
            Tuple[StepResult, Container]: Failure or success of the package installation and the connector under test container (with the connector package installed).
        """
        connector_under_test = await environments.with_installed_airbyte_connector(self.context)
        return await self.get_step_result(connector_under_test), connector_under_test


class PythonTests(Step, ABC):
    def pytest_logs_to_step_result(self, logs: str) -> StepResult:
        last_log_line = logs.split("\n")[-2]
        if "failed" in last_log_line:
            return StepResult(self, StepStatus.FAILURE, stderr=logs)
        elif "no tests ran" in last_log_line:
            return StepResult(self, StepStatus.SKIPPED, stdout=logs)
        else:
            return StepResult(self, StepStatus.SUCCESS, stdout=logs)

    async def _run_tests_in_directory(self, connector_under_test: Container, test_directory: str) -> StepResult:
        """Runs the pytest tests in the test_directory that was passed.
        A StepStatus.SKIPPED is returned if no tests were discovered.
        Args:
            connector_under_test (Container): The connector under test container.
            test_directory (str): The directory in which the python test modules are declared

        Returns:
            Tuple[StepStatus, Optional[str], Optional[str]]: Tuple of StepStatus, stderr and stdout.
        """
        test_config = (
            "pytest.ini" if await check_path_in_workdir(connector_under_test, "pytest.ini") else "/" + environments.PYPROJECT_TOML_FILE_PATH
        )
        if await check_path_in_workdir(connector_under_test, test_directory):
            tester = connector_under_test.with_exec(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--suppress-tests-failed-exit-code",
                    "--suppress-no-test-exit-code",
                    "-s",
                    test_directory,
                    "-c",
                    test_config,
                ]
            )
            return self.pytest_logs_to_step_result(await tester.stdout())

        else:
            return StepResult(self, StepStatus.SKIPPED)


class AcceptanceTests(PythonTests):
    title = "Acceptance tests"

    async def _run(self) -> StepResult:
        """Runs the acceptance test suite on a connector dev image.
        It's rebuilding the connector acceptance test image if the tag is :dev.
        It's building the connector under test dev image if the connector image is :dev in the acceptance test config.

        Returns:
            StepResult: Failure or success of the acceptances tests with stdout and stdout.
        """
        if not self.context.connector.acceptance_test_config:
            return StepResult(self, StepStatus.SKIPPED), None

        dagger_client = self.get_dagger_pipeline(self.context.dagger_client)

        if self.context.connector_acceptance_test_image.endswith(":dev"):
            cat_container = self.context.connector_acceptance_test_source_dir.docker_build()
        else:
            cat_container = dagger_client.container().from_(self.context.connector_acceptance_test_image)

        dockerd = (
            dagger_client.container()
            .from_("docker:23.0.1-dind")
            .with_mounted_cache("/var/lib/docker", dagger_client.cache_volume("docker-lib"), sharing=CacheSharingMode.PRIVATE)
            .with_mounted_cache("/tmp", dagger_client.cache_volume("share-tmp"))
            .with_exposed_port(2375)
            .with_exec(["dockerd", "--log-level=error", "--host=tcp://0.0.0.0:2375", "--tls=false"], insecure_root_capabilities=True)
        )
        docker_host = await dockerd.endpoint(scheme="tcp")

        acceptance_test_cache_buster = str(uuid.uuid4())
        if self.context.connector.acceptance_test_config["connector_image"].endswith(":dev"):
            inspect_output = await (
                dagger_client.pipeline(f"Building {self.context.connector.acceptance_test_config['connector_image']}")
                .container()
                .from_("docker:23.0.1-cli")
                .with_env_variable("DOCKER_HOST", docker_host)
                .with_service_binding("docker", dockerd)
                .with_mounted_directory("/connector_to_build", self.context.get_connector_dir(exclude=[".venv"]))
                .with_workdir("/connector_to_build")
                .with_exec(["docker", "build", ".", "-t", f"airbyte/{self.context.connector.technical_name}:dev"])
                .with_exec(["docker", "image", "inspect", f"airbyte/{self.context.connector.technical_name}:dev"])
                .stdout()
            )
            acceptance_test_cache_buster = json.loads(inspect_output)[0]["Id"]

        cat_container = (
            cat_container.with_env_variable("DOCKER_HOST", docker_host)
            .with_entrypoint(["pip"])
            .with_exec(["install", "pytest-custom_exit_code"])
            .with_service_binding("docker", dockerd)
            .with_mounted_cache("/tmp", dagger_client.cache_volume("share-tmp"))
            .with_mounted_directory("/test_input", self.context.get_connector_dir(exclude=["secrets", ".venv"]))
            .with_directory("/test_input/secrets", self.context.secrets_dir)
            .with_workdir("/test_input")
            .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "--suppress-tests-failed-exit-code"])
            .with_env_variable("CACHEBUSTER", acceptance_test_cache_buster)
            .with_exec(["--acceptance-test-config", "/test_input"])
        )

        secret_dir = cat_container.directory("/test_input/secrets")

        async with asyncer.create_task_group() as task_group:
            soon_secret_files = task_group.soonify(secret_dir.entries)()
            soon_cat_container_stdout = task_group.soonify(cat_container.stdout)()

        if secret_files := soon_secret_files.value:
            for file_path in secret_files:
                if file_path.startswith("updated_configurations"):
                    self.context.updated_secrets_dir = secret_dir
                    break

        return self.pytest_logs_to_step_result(soon_cat_container_stdout.value)


class UnitTests(PythonTests):
    title = "Unit tests"

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the unit_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the unit tests with stdout and stdout.
        """
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        return await self._run_tests_in_directory(connector_under_test, "unit_tests")


class IntegrationTests(PythonTests):
    title = "Integration tests"

    async def _run(self, connector_under_test: Container) -> StepResult:
        """Run all pytest tests declared in the integration_tests directory of the connector code.

        Args:
            connector_under_test (Container): The connector under test container.

        Returns:
            StepResult: Failure or success of the integration tests with stdout and stdout.
        """
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        connector_under_test_with_secrets = connector_under_test.with_directory(
            f"{self.context.connector.code_directory}/secrets", self.context.secrets_dir
        )

        return await self._run_tests_in_directory(connector_under_test_with_secrets, "integration_tests")


async def run_all_tests(context: ConnectorTestContext) -> List[StepResult]:
    package_install_results, connector_under_test = await ConnectorInstallTest(context).run()
    unit_tests_results = await UnitTests(context).run(connector_under_test)
    results = [
        package_install_results,
        unit_tests_results,
    ]
    if unit_tests_results.status is StepStatus.FAILURE:
        return results + [IntegrationTests(context).skip(), AcceptanceTests(context).skip()]

    context.secrets_dir = await secrets.get_connector_secret_dir(context)
    async with asyncer.create_task_group() as task_group:
        tasks = [
            task_group.soonify(IntegrationTests(context).run)(connector_under_test),
            task_group.soonify(AcceptanceTests(context).run)(),
        ]

    return results + [task.value for task in tasks]
