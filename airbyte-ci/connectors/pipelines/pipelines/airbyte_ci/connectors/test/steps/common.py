#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests agnostic to a connector language."""

import datetime
import os
import time
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import ClassVar, List, Optional

import requests  # type: ignore
import semver
import yaml  # type: ignore
from dagger import Container, Directory
from pipelines import hacks, main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.consts import INTERNAL_TOOL_PATHS, CIContext
from pipelines.dagger.actions import secrets
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.utils import METADATA_FILE_NAME, get_exec_result
from pipelines.models.secrets import Secret
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
            secret_env_variables={"DOCKER_HUB_USERNAME": context.docker_hub_username, "DOCKER_HUB_PASSWORD": context.docker_hub_password}
            if context.docker_hub_username and context.docker_hub_password
            else None,
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

    def __init__(self, context: ConnectorContext, secrets: List[Secret], concurrent_test_run: Optional[bool] = False) -> None:
        """Create a step to run acceptance tests for a connector if it has an acceptance test config file.

        Args:
            context (ConnectorContext): The current test context, providing a connector object, a dagger client and a repository directory.
            secrets (List[Secret]): List of secrets to mount to the connector container under test.
            concurrent_test_run (Optional[bool], optional): Whether to run acceptance tests in parallel. Defaults to False.
        """
        super().__init__(context, secrets)
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
            .with_(await secrets.mounted_connector_secrets(self.context, self.CONTAINER_SECRETS_DIRECTORY, self.secrets))
        )
        if "_EXPERIMENTAL_DAGGER_RUNNER_HOST" in os.environ:
            self.context.logger.info("Using experimental dagger runner host to run CAT with dagger-in-dagger")
            cat_container = cat_container.with_env_variable(
                "_EXPERIMENTAL_DAGGER_RUNNER_HOST", "unix:///var/run/buildkit/buildkitd.sock"
            ).with_unix_socket(
                "/var/run/buildkit/buildkitd.sock", self.context.dagger_client.host().unix_socket("/var/run/buildkit/buildkitd.sock")
            )

        return cat_container.with_unix_socket("/var/run/docker.sock", self.context.dagger_client.host().unix_socket("/var/run/docker.sock"))


class RegressionTests(Step):
    """A step to run regression tests for a connector."""

    context: ConnectorContext
    title = "Regression tests"
    skipped_exit_code = 5
    accept_extra_params = True
    regression_tests_artifacts_dir = Path("/tmp/regression_tests_artifacts")
    working_directory = "/app"
    github_user = "octavia-squidington-iii"
    platform_repo_url = "airbytehq/airbyte-platform-internal"

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

    def regression_tests_command(self) -> List[str]:
        """
        This command:

        1. Starts a Google Cloud SQL proxy running on localhost, which is used by the connection-retriever to connect to postgres.
        2. Gets the PID of the proxy so it can be killed once done.
        3. Runs the regression tests.
        4. Kills the proxy, and waits for it to exit.
        5. Exits with the regression tests' exit code.
        We need to explicitly kill the proxy in order to allow the GitHub Action to exit.
        An alternative that we can consider is to run the proxy as a separate service.

        (See https://docs.dagger.io/manuals/developer/python/328492/services/ and https://cloud.google.com/sql/docs/postgres/sql-proxy#cloud-sql-auth-proxy-docker-image)
        """
        run_proxy = "./cloud-sql-proxy prod-ab-cloud-proj:us-west3:prod-pgsql-replica --credentials-file /tmp/credentials.json"
        run_pytest = " ".join(
            [
                "poetry",
                "run",
                "pytest",
                "src/live_tests/regression_tests",
                "--connector-image",
                self.connector_image,
                "--connection-id",
                self.connection_id or "",
                "--control-version",
                self.control_version or "",
                "--target-version",
                self.target_version or "",
                "--pr-url",
                self.pr_url or "",
                "--run-id",
                self.run_id or "",
                "--should-read-with-state",
                str(self.should_read_with_state),
            ]
        )
        run_pytest_with_proxy = dedent(
            f"""
        {run_proxy} &
        proxy_pid=$!
        {run_pytest}
        pytest_exit=$?
        kill $proxy_pid
        wait $proxy_pid
        exit $pytest_exit
        """
        )
        return ["bash", "-c", f"'{run_pytest_with_proxy}'"]

    def __init__(self, context: ConnectorContext) -> None:
        """Create a step to run regression tests for a connector.

        Args:
            context (ConnectorContext): The current test context, providing a connector object, a dagger client and a repository directory.
        """
        super().__init__(context)
        self.connector_image = context.docker_image.split(":")[0]
        options = self.context.run_step_options.step_params.get(CONNECTOR_TEST_STEP_ID.CONNECTOR_REGRESSION_TESTS, {})

        self.connection_id = self.context.run_step_options.get_item_or_default(options, "connection-id", None)
        self.pr_url = self.context.run_step_options.get_item_or_default(options, "pr-url", None)

        if not self.connection_id and self.pr_url:
            raise ValueError("`connection-id` and `pr-url` are required to run regression tests.")

        self.control_version = self.context.run_step_options.get_item_or_default(options, "control-version", "latest")
        self.target_version = self.context.run_step_options.get_item_or_default(options, "target-version", "dev")
        self.should_read_with_state = self.context.run_step_options.get_item_or_default(options, "should-read-with-state", True)
        self.run_id = os.getenv("GITHUB_RUN_ID") or str(int(time.time()))

    async def _run(self, connector_under_test_container: Container) -> StepResult:
        """Run the regression test suite.

        Args:
            connector_under_test (Container): The container holding the target connector test image.

        Returns:
            StepResult: Failure or success of the regression tests with stdout and stderr.
        """
        container = await self._build_regression_test_container(await connector_under_test_container.id())
        container = container.with_(hacks.never_fail_exec(self.regression_tests_command()))
        regression_tests_artifacts_dir = str(self.regression_tests_artifacts_dir)
        path_to_report = f"{regression_tests_artifacts_dir}/session_{self.run_id}/report.html"

        exit_code, stdout, stderr = await get_exec_result(container)

        if "report.html" not in await container.directory(f"{regression_tests_artifacts_dir}/session_{self.run_id}").entries():
            main_logger.exception(
                "The report file was not generated, an unhandled error likely happened during regression test execution, please check the step stderr and stdout for more details"
            )
            regression_test_report = None
        else:
            await container.file(path_to_report).export(path_to_report)
            with open(path_to_report, "r") as fp:
                regression_test_report = fp.read()

        return StepResult(
            step=self,
            status=self.get_step_status_from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output=container,
            report=regression_test_report,
        )

    async def _build_regression_test_container(self, target_container_id: str) -> Container:
        """Create a container to run regression tests."""
        container = with_poetry(self.context)
        container_requirements = ["apt-get", "install", "-y", "git", "curl", "docker.io"]
        if not self.context.is_ci:
            # Outside of CI we use ssh to get the connection-retriever package from airbyte-platform-internal
            container_requirements += ["openssh-client"]
        container = (
            container.with_exec(["apt-get", "update"])
            .with_exec(container_requirements)
            .with_exec(["bash", "-c", "curl https://sdk.cloud.google.com | bash"])
            .with_env_variable("PATH", "/root/google-cloud-sdk/bin:$PATH", expand=True)
            .with_mounted_directory("/app", self.context.live_tests_dir)
            .with_workdir("/app")
            # Enable dagger-in-dagger
            .with_unix_socket("/var/run/docker.sock", self.dagger_client.host().unix_socket("/var/run/docker.sock"))
            .with_env_variable("RUN_IN_AIRBYTE_CI", "1")
            # The connector being tested is already built and is stored in a location accessible to an inner dagger kicked off by
            # regression tests. The connector can be found if you know the container ID, so we write the container ID to a file and put
            # it in the regression test container. This way regression tests will use the already-built connector instead of trying to
            # build their own.
            .with_new_file("/tmp/container_id.txt", contents=str(target_container_id))
        )

        if self.context.is_ci:
            container = (
                container
                # In CI, use https to get the connection-retriever package from airbyte-platform-internal instead of ssh
                .with_exec(
                    [
                        "sed",
                        "-i",
                        "-E",
                        rf"s,git@github\.com:{self.platform_repo_url},https://github.com/{self.platform_repo_url}.git,",
                        "pyproject.toml",
                    ]
                )
                .with_exec(
                    [
                        "poetry",
                        "source",
                        "add",
                        "--priority=supplemental",
                        "airbyte-platform-internal-source",
                        "https://github.com/airbytehq/airbyte-platform-internal.git",
                    ]
                )
                .with_exec(
                    [
                        "poetry",
                        "config",
                        "http-basic.airbyte-platform-internal-source",
                        self.github_user,
                        self.context.ci_github_access_token.value if self.context.ci_github_access_token else "",
                    ]
                )
                # Add GCP credentials from the environment and point google to their location (also required for connection-retriever)
                .with_new_file("/tmp/credentials.json", contents=os.getenv("GCP_INTEGRATION_TESTER_CREDENTIALS"))
                .with_env_variable("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/credentials.json")
                .with_exec(
                    [
                        "curl",
                        "-o",
                        "cloud-sql-proxy",
                        "https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.0/cloud-sql-proxy.linux.amd64",
                    ]
                )
                .with_exec(
                    [
                        "chmod",
                        "+x",
                        "cloud-sql-proxy",
                    ]
                )
                .with_env_variable("CI", "1")
            )

        else:
            container = (
                container.with_mounted_file("/root/.ssh/id_rsa", self.dagger_client.host().file(str(Path("~/.ssh/id_rsa").expanduser())))
                .with_mounted_file("/root/.ssh/known_hosts", self.dagger_client.host().file(str(Path("~/.ssh/known_hosts").expanduser())))
                .with_mounted_file(
                    "/root/.config/gcloud/application_default_credentials.json",
                    self.dagger_client.host().file(str(Path("~/.config/gcloud/application_default_credentials.json").expanduser())),
                )
            )

        container = container.with_exec(["poetry", "lock", "--no-update"]).with_exec(["poetry", "install"])
        return container
