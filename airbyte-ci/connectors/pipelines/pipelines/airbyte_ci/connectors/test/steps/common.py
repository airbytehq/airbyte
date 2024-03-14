#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests agnostic to a connector language."""

import datetime
import os
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import ClassVar, List, Optional

import requests  # type: ignore
import semver
import yaml  # type: ignore
from dagger import Container, Directory
from pipelines import hacks
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.consts import INTERNAL_TOOL_PATHS, CIContext
from pipelines.dagger.actions import secrets
from pipelines.helpers.utils import METADATA_FILE_NAME
from pipelines.models.steps import STEP_PARAMS, MountPath, Step, StepResult, StepStatus


class VersionCheck(Step, ABC):
    """A step to validate the connector version was bumped if files were modified"""

    context: ConnectorContext
    GITHUB_URL_PREFIX_FOR_CONNECTORS = "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors"
    failure_message: ClassVar

    @property
    def should_run(self) -> bool:
        return True

    @property
    def github_master_metadata_url(self) -> str:
        return f"{self.GITHUB_URL_PREFIX_FOR_CONNECTORS}/{self.context.connector.technical_name}/{METADATA_FILE_NAME}"

    @cached_property
    def master_metadata(self) -> Optional[dict]:
        response = requests.get(self.github_master_metadata_url)

        # New connectors will not have a metadata file in master
        if not response.ok:
            return None
        return yaml.safe_load(response.text)

    @property
    def master_connector_version(self) -> semver.Version:
        metadata = self.master_metadata
        if not metadata:
            return semver.Version.parse("0.0.0")

        return semver.Version.parse(str(metadata["data"]["dockerImageTag"]))

    @property
    def current_connector_version(self) -> semver.Version:
        return semver.Version.parse(str(self.context.metadata["dockerImageTag"]))

    @property
    def success_result(self) -> StepResult:
        return StepResult(step=self, status=StepStatus.SUCCESS)

    @property
    def failure_result(self) -> StepResult:
        return StepResult(step=self, status=StepStatus.FAILURE, stderr=self.failure_message)

    @abstractmethod
    def validate(self) -> StepResult:
        raise NotImplementedError()

    async def _run(self) -> StepResult:
        if not self.should_run:
            return StepResult(step=self, status=StepStatus.SKIPPED, stdout="No modified files required a version bump.")
        if self.context.ci_context == CIContext.MASTER:
            return StepResult(step=self, status=StepStatus.SKIPPED, stdout="Version check are not running in master context.")
        try:
            return self.validate()
        except (requests.HTTPError, ValueError, TypeError) as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))


class VersionIncrementCheck(VersionCheck):
    context: ConnectorContext
    title = "Connector version increment check"

    BYPASS_CHECK_FOR = [
        METADATA_FILE_NAME,
        "acceptance-test-config.yml",
        "README.md",
        "bootstrap.md",
        ".dockerignore",
        "unit_tests",
        "integration_tests",
        "src/test",
        "src/test-integration",
        "src/test-performance",
        "build.gradle",
    ]

    @property
    def failure_message(self) -> str:
        return f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented. The files you modified should lead to a version bump. Master version is {self.master_connector_version}, current version is {self.current_connector_version}"

    @property
    def should_run(self) -> bool:
        for filename in self.context.modified_files:
            relative_path = str(filename).replace(str(self.context.connector.code_directory) + "/", "")
            if not any([relative_path.startswith(to_bypass) for to_bypass in self.BYPASS_CHECK_FOR]):
                return True
        return False

    def validate(self) -> StepResult:
        if not self.current_connector_version > self.master_connector_version:
            return self.failure_result
        return self.success_result


class QaChecks(SimpleDockerStep):
    """A step to run QA checks for a connectors.
    More details in https://github.com/airbytehq/airbyte/blob/main/airbyte-ci/connectors/connectors_qa/README.md
    """

    def __init__(self, context: ConnectorContext) -> None:
        code_directory = context.connector.code_directory
        documentation_file_path = context.connector.documentation_file_path
        migration_guide_file_path = context.connector.migration_guide_file_path
        icon_path = context.connector.icon_path
        technical_name = context.connector.technical_name

        # When the connector is strict-encrypt, we should run QA checks on the main one as it's the one whose artifacts gets released
        if context.connector.technical_name.endswith("-strict-encrypt"):
            technical_name = technical_name.replace("-strict-encrypt", "")
            code_directory = Path(str(code_directory).replace("-strict-encrypt", ""))
            if documentation_file_path:
                documentation_file_path = Path(str(documentation_file_path).replace("-strict-encrypt", ""))
            if migration_guide_file_path:
                migration_guide_file_path = Path(str(migration_guide_file_path).replace("-strict-encrypt", ""))
            if icon_path:
                icon_path = Path(str(icon_path).replace("-strict-encrypt", ""))

        super().__init__(
            title=f"Run QA checks for {technical_name}",
            context=context,
            paths_to_mount=[
                MountPath(code_directory),
                # These paths are optional
                # But their absence might make the QA check fail
                MountPath(documentation_file_path, optional=True),
                MountPath(migration_guide_file_path, optional=True),
                MountPath(icon_path, optional=True),
            ],
            internal_tools=[
                MountPath(INTERNAL_TOOL_PATHS.CONNECTORS_QA.value),
            ],
            secrets={
                k: v
                for k, v in {
                    "DOCKER_HUB_USERNAME": context.docker_hub_username_secret,
                    "DOCKER_HUB_PASSWORD": context.docker_hub_password_secret,
                }.items()
                if v
            },
            command=["connectors-qa", "run", f"--name={technical_name}"],
        )


class AcceptanceTests(Step):
    """A step to run acceptance tests for a connector if it has an acceptance test config file."""

    context: ConnectorContext
    title = "Acceptance tests"
    CONTAINER_TEST_INPUT_DIRECTORY = "/test_input"
    CONTAINER_SECRETS_DIRECTORY = "/test_input/secrets"
    skipped_exit_code = 5
    accept_extra_params = True

    @property
    def default_params(self) -> STEP_PARAMS:
        """Default pytest options.

        Returns:
            dict: The default pytest options.
        """
        return super().default_params | {
            "-ra": [],  # Show extra test summary info in the report for all but the passed tests
            "--disable-warnings": [],  # Disable warnings in the pytest report
            "--durations": ["3"],  # Show the 3 slowest tests in the report
        }

    @property
    def base_cat_command(self) -> List[str]:
        command = [
            "python",
            "-m",
            "pytest",
            "-p",  # Load the connector_acceptance_test plugin
            "connector_acceptance_test.plugin",
            "--acceptance-test-config",
            self.CONTAINER_TEST_INPUT_DIRECTORY,
        ]

        if self.concurrent_test_run:
            command += ["--numprocesses=auto"]  # Using pytest-xdist to run tests in parallel, auto means using all available cores
        return command

    def __init__(self, context: ConnectorContext, concurrent_test_run: Optional[bool] = False) -> None:
        """Create a step to run acceptance tests for a connector if it has an acceptance test config file.

        Args:
            context (ConnectorContext): The current test context, providing a connector object, a dagger client and a repository directory.
            concurrent_test_run (Optional[bool], optional): Whether to run acceptance tests in parallel. Defaults to False.
        """
        super().__init__(context)
        self.concurrent_test_run = concurrent_test_run

    async def get_cat_command(self, connector_dir: Directory) -> List[str]:
        """
        Connectors can optionally setup or teardown resources before and after the acceptance tests are run.
        This is done via the acceptance.py file in their integration_tests directory.
        We append this module as a plugin the acceptance will use.
        """
        cat_command = self.base_cat_command
        if "integration_tests" in await connector_dir.entries():
            if "acceptance.py" in await connector_dir.directory("integration_tests").entries():
                cat_command += ["-p", "integration_tests.acceptance"]
        return cat_command + self.params_as_cli_options

    async def _run(self, connector_under_test_container: Container) -> StepResult:
        """Run the acceptance test suite on a connector dev image. Build the connector acceptance test image if the tag is :dev.

        Args:
            connector_under_test_container (Container): The container holding the connector under test image.

        Returns:
            StepResult: Failure or success of the acceptances tests with stdout and stderr.
        """

        if not self.context.connector.acceptance_test_config:
            return StepResult(step=self, status=StepStatus.SKIPPED)
        connector_dir = await self.context.get_connector_dir()
        cat_container = await self._build_connector_acceptance_test(connector_under_test_container, connector_dir)
        cat_command = await self.get_cat_command(connector_dir)
        cat_container = cat_container.with_(hacks.never_fail_exec(cat_command))
        step_result = await self.get_step_result(cat_container)
        secret_dir = cat_container.directory(self.CONTAINER_SECRETS_DIRECTORY)

        if secret_files := await secret_dir.entries():
            for file_path in secret_files:
                if file_path.startswith("updated_configurations"):
                    self.context.updated_secrets_dir = secret_dir
                    break
        return step_result

    def get_cache_buster(self) -> str:
        """
        This bursts the CAT cached results everyday and on new version or image size change.
        It's cool because in case of a partially failing nightly build the connectors that already ran CAT won't re-run CAT.
        We keep the guarantee that a CAT runs everyday.

        Returns:
            str: A string representing the cachebuster value.
        """
        return datetime.datetime.utcnow().strftime("%Y%m%d") + self.context.connector.version

    async def _build_connector_acceptance_test(self, connector_under_test_container: Container, test_input: Directory) -> Container:
        """Create a container to run connector acceptance tests.

        Args:
            connector_under_test_container (Container): The container holding the connector under test image.
            test_input (Directory): The connector under test directory.
        Returns:
            Container: A container with connector acceptance tests installed.
        """

        if self.context.connector_acceptance_test_image.endswith(":dev"):
            cat_container = self.context.connector_acceptance_test_source_dir.docker_build()
        else:
            cat_container = self.dagger_client.container().from_(self.context.connector_acceptance_test_image)

        connector_container_id = await connector_under_test_container.id()

        cat_container = (
            cat_container.with_env_variable("RUN_IN_AIRBYTE_CI", "1")
            .with_exec(["mkdir", "/dagger_share"], skip_entrypoint=True)
            .with_env_variable("CACHEBUSTER", self.get_cache_buster())
            .with_new_file("/tmp/container_id.txt", contents=str(connector_container_id))
            .with_workdir("/test_input")
            .with_mounted_directory("/test_input", test_input)
            .with_(await secrets.mounted_connector_secrets(self.context, self.CONTAINER_SECRETS_DIRECTORY))
        )
        if "_EXPERIMENTAL_DAGGER_RUNNER_HOST" in os.environ:
            self.context.logger.info("Using experimental dagger runner host to run CAT with dagger-in-dagger")
            cat_container = cat_container.with_env_variable(
                "_EXPERIMENTAL_DAGGER_RUNNER_HOST", "unix:///var/run/buildkit/buildkitd.sock"
            ).with_unix_socket(
                "/var/run/buildkit/buildkitd.sock", self.context.dagger_client.host().unix_socket("/var/run/buildkit/buildkitd.sock")
            )

        return cat_container.with_unix_socket("/var/run/docker.sock", self.context.dagger_client.host().unix_socket("/var/run/docker.sock"))
