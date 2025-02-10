#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests agnostic to a connector language."""

import datetime
import json
import os
import time
from abc import ABC, abstractmethod
from enum import Enum
from functools import cached_property
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, List, Optional, Set

import dagger
import requests  # type: ignore
import semver
import yaml  # type: ignore
from dagger import Container, Directory

# This slugify lib has to be consistent with the slugify lib used in live_tests
# live_test can't resolve the passed connector container otherwise.
from slugify import slugify  # type: ignore

from pipelines import hacks, main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.steps.docker import SimpleDockerStep
from pipelines.consts import INTERNAL_TOOL_PATHS, CIContext
from pipelines.dagger.actions import secrets
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.github import AIRBYTE_GITHUBUSERCONTENT_URL_PREFIX
from pipelines.helpers.utils import METADATA_FILE_NAME, get_exec_result
from pipelines.models.artifacts import Artifact
from pipelines.models.secrets import Secret
from pipelines.models.steps import STEP_PARAMS, MountPath, Step, StepResult, StepStatus

GITHUB_URL_PREFIX_FOR_CONNECTORS = f"{AIRBYTE_GITHUBUSERCONTENT_URL_PREFIX}/master/airbyte-integrations/connectors"


class VersionCheck(Step, ABC):
    """A step to validate the connector version was bumped if files were modified"""

    context: ConnectorContext

    @property
    def should_run(self) -> bool:
        return True

    @property
    def github_master_metadata_url(self) -> str:
        return f"{GITHUB_URL_PREFIX_FOR_CONNECTORS}/{self.context.connector.technical_name}/{METADATA_FILE_NAME}"

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

    def _get_failure_result(self, failure_message: str) -> StepResult:
        return StepResult(step=self, status=StepStatus.FAILURE, stderr=failure_message)

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
        "erd",
        "build_customization.py",
    ]

    @property
    def should_run(self) -> bool:
        for filename in self.context.modified_files:
            relative_path = str(filename).replace(str(self.context.connector.code_directory) + "/", "")
            if not any([relative_path.startswith(to_bypass) for to_bypass in self.BYPASS_CHECK_FOR]):
                return True
        return False

    def is_version_not_incremented(self) -> bool:
        return self.master_connector_version >= self.current_connector_version

    def get_failure_message_for_no_increment(self) -> str:
        return (
            f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented. "
            f"Master version is {self.master_connector_version}, current version is {self.current_connector_version}"
        )

    def are_both_versions_release_candidates(self) -> bool:
        return bool(
            self.master_connector_version.prerelease
            and self.current_connector_version.prerelease
            and "rc" in self.master_connector_version.prerelease
            and "rc" in self.current_connector_version.prerelease
        )

    def have_same_major_minor_patch(self) -> bool:
        return (
            self.master_connector_version.major == self.current_connector_version.major
            and self.master_connector_version.minor == self.current_connector_version.minor
            and self.master_connector_version.patch == self.current_connector_version.patch
        )

    def validate(self) -> StepResult:
        if self.is_version_not_incremented():
            return self._get_failure_result(
                (
                    f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented. "
                    f"Master version is {self.master_connector_version}, current version is {self.current_connector_version}"
                )
            )

        if self.are_both_versions_release_candidates():
            if not self.have_same_major_minor_patch():
                return self._get_failure_result(
                    (
                        f"Master and current version are release candidates but they have different major, minor or patch versions. "
                        f"Release candidates should only differ in the prerelease part. Master version is {self.master_connector_version}, "
                        f"current version is {self.current_connector_version}"
                    )
                )

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
    REPORT_LOG_PATH = "/tmp/report_log.jsonl"
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
            # Write the test report in jsonl format
            f"--report-log={self.REPORT_LOG_PATH}",
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
            .with_exec(["mkdir", "/dagger_share"])
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

    def get_is_hard_failure(self) -> bool:
        """When a connector is not certified or the CI context is master, we consider the acceptance tests as hard failures:
        The overall status of the pipeline will be FAILURE if the acceptance tests fail.
        For marketplace connectors we defer to the IncrementalAcceptanceTests step to determine if the acceptance tests are hard failures:
        If a new test is failing compared to the released version of the connector.

        Returns:
            bool: Whether a failure of acceptance tests should be considered a hard failures.
        """
        return self.context.connector.metadata.get("supportLevel") == "certified" or self.context.ci_context == CIContext.MASTER

    async def get_step_result(self, container: Container) -> StepResult:
        """Retrieve stdout, stderr and exit code from the executed CAT container.
        Pull the report logs from the container and create an Artifact object from it.
        Build and return a step result object from these objects.

        Args:
            container (Container): The CAT container to get the results from.

        Returns:
            StepResult: The step result object.
        """
        exit_code, stdout, stderr = await get_exec_result(container)
        report_log_artifact = Artifact(
            name="cat_report_log.jsonl",
            content_type="text/jsonl",
            content=container.file(self.REPORT_LOG_PATH),
            to_upload=True,
        )
        status = self.get_step_status_from_exit_code(exit_code)

        is_hard_failure = status is StepStatus.FAILURE and self.get_is_hard_failure()

        return StepResult(
            step=self,
            status=self.get_step_status_from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output={"report_log": report_log_artifact},
            artifacts=[report_log_artifact],
            consider_in_overall_status=status is StepStatus.SUCCESS or is_hard_failure,
        )


class IncrementalAcceptanceTests(Step):
    """This step runs the acceptance tests on the released image of the connector and compares the results with the current acceptance tests report log.
    It fails if there are new failing tests in the current acceptance tests report log.
    """

    title = "Incremental Acceptance Tests"
    context: ConnectorContext

    async def get_failed_pytest_node_ids(self, current_acceptance_tests_report_log: Artifact) -> Set[str]:
        """Parse the report log of the acceptance tests and return the pytest node ids of the failed tests.

        Args:
            current_acceptance_tests_report_log (Artifact): The report log of the acceptance tests.

        Returns:
            List[str]: The pytest node ids of the failed tests.
        """
        current_report_lines = (await current_acceptance_tests_report_log.content.contents()).splitlines()
        failed_nodes = set()
        for line in current_report_lines:
            single_test_report = json.loads(line)
            if "nodeid" not in single_test_report or "outcome" not in single_test_report:
                continue
            if single_test_report["outcome"] == "failed":
                failed_nodes.add(single_test_report["nodeid"])
        return failed_nodes

    def _get_master_metadata(self) -> Dict[str, Any]:
        metadata_response = requests.get(f"{GITHUB_URL_PREFIX_FOR_CONNECTORS}/{self.context.connector.technical_name}/metadata.yaml")
        if not metadata_response.ok:
            raise FileNotFoundError(f"Could not fetch metadata file for {self.context.connector.technical_name} on master.")
        return yaml.safe_load(metadata_response.text)

    async def get_result_log_on_master(self, master_metadata: dict) -> Artifact:
        """Runs acceptance test on the released image of the connector and returns the report log.
        The released image version is fetched from the master metadata file of the connector.
        We're not using the online connector registry here as some connectors might not be released to OSS nor Airbyte Cloud.
        Thanks to Dagger caching subsequent runs of this step will be cached if the released image did not change.

        Returns:
            Artifact: The report log of the acceptance tests run on the released image.
        """
        master_docker_image_tag = master_metadata["data"]["dockerImageTag"]
        released_image = f'{master_metadata["data"]["dockerRepository"]}:{master_docker_image_tag}'
        released_container = self.dagger_client.container().from_(released_image)
        self.logger.info(f"Running acceptance tests on released image: {released_image}")
        acceptance_tests_results_on_master = await AcceptanceTests(self.context, self.secrets).run(released_container)
        return acceptance_tests_results_on_master.output["report_log"]

    async def _run(self, current_acceptance_tests_result: StepResult) -> StepResult:
        """Compare the acceptance tests report log of the current image with the one of the released image.
        Fails if there are new failing tests in the current acceptance tests report log.
        """

        if current_acceptance_tests_result.consider_in_overall_status:
            return StepResult(
                step=self, status=StepStatus.SKIPPED, stdout="Skipping because the current acceptance tests are hard failures."
            )

        current_acceptance_tests_report_log = current_acceptance_tests_result.output["report_log"]
        current_failing_nodes = await self.get_failed_pytest_node_ids(current_acceptance_tests_report_log)
        if not current_failing_nodes:
            return StepResult(
                step=self, status=StepStatus.SKIPPED, stdout="No failing acceptance tests were detected on the current version."
            )
        try:
            master_metadata = self._get_master_metadata()
        except FileNotFoundError as exc:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="The connector does not have a metadata file on master. Skipping incremental acceptance tests.",
                exc_info=exc,
            )

        master_result_logs = await self.get_result_log_on_master(master_metadata)

        master_failings = await self.get_failed_pytest_node_ids(master_result_logs)
        new_failing_nodes = current_failing_nodes - master_failings
        if not new_failing_nodes:
            return StepResult(
                step=self,
                status=StepStatus.SUCCESS,
                stdout=dedent(
                    f"""
                No new failing acceptance tests were detected. 
                Acceptance tests are still failing with {len(current_failing_nodes)} failing tests but the AcceptanceTests step is not a hard failure for this connector.
                Please checkout the original acceptance tests failures and assess how critical they are.
                """
                ),
            )
        else:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stdout=f"{len(new_failing_nodes)} new failing acceptance tests detected:\n-"
                + "\n-".join(current_failing_nodes)
                + "\nPlease fix the new failing tests before merging this PR."
                + f"\nPlease also check the original {len(current_failing_nodes)} acceptance tests failures and assess how critical they are.",
            )


class LiveTestSuite(Enum):
    ALL = "live"
    REGRESSION = "regression"
    VALIDATION = "validation"


class LiveTests(Step):
    """A step to run live tests for a connector."""

    context: ConnectorContext
    skipped_exit_code = 5
    accept_extra_params = True
    local_tests_artifacts_dir = Path("/tmp/live_tests_artifacts")
    working_directory = "/app"
    github_user = "octavia-squidington-iii"
    platform_repo_url = "airbytehq/airbyte-platform-internal"
    test_suite_to_dir = {
        LiveTestSuite.ALL: "src/live_tests",
        LiveTestSuite.REGRESSION: "src/live_tests/regression_tests",
        LiveTestSuite.VALIDATION: "src/live_tests/validation_tests",
    }

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
    def title(self) -> str:
        return f"Connector {self.test_suite.title()} Tests"

    def _test_command(self) -> List[str]:
        """
        The command used to run the tests
        """
        base_command = [
            "poetry",
            "run",
            "pytest",
            self.test_dir,
            "--connector-image",
            self.connector_image,
        ]
        return base_command + self._get_command_options()

    def _get_command_options(self) -> List[str]:
        command_options = []
        if self.connection_id:
            command_options += ["--connection-id", self.connection_id]
        if self.control_version:
            command_options += ["--control-version", self.control_version]
        if self.target_version:
            command_options += ["--target-version", self.target_version]
        if self.pr_url:
            command_options += ["--pr-url", self.pr_url]
        if self.run_id:
            command_options += ["--run-id", self.run_id]
        if self.should_read_with_state:
            command_options += ["--should-read-with-state=1"]
        if self.disable_proxy:
            command_options += ["--disable-proxy=1"]
        if self.test_evaluation_mode:
            command_options += ["--test-evaluation-mode", self.test_evaluation_mode]
        if self.selected_streams:
            command_options += ["--stream", self.selected_streams]
        command_options += ["--connection-subset", self.connection_subset]
        return command_options

    def _run_command_with_proxy(self, command: str) -> List[str]:
        """
        This command:

        1. Starts a Google Cloud SQL proxy running on localhost, which is used by the connection-retriever to connect to postgres.
           This is required for secure access to our internal tools.
        2. Gets the PID of the proxy so it can be killed once done.
        3. Runs the command that was passed in as input.
        4. Kills the proxy, and waits for it to exit.
        5. Exits with the command's exit code.
        We need to explicitly kill the proxy in order to allow the GitHub Action to exit.
        An alternative that we can consider is to run the proxy as a separate service.

        (See https://docs.dagger.io/manuals/developer/python/328492/services/ and https://cloud.google.com/sql/docs/postgres/sql-proxy#cloud-sql-auth-proxy-docker-image)
        """
        run_proxy = "./cloud-sql-proxy prod-ab-cloud-proj:us-west3:prod-pgsql-replica --credentials-file /tmp/credentials.json"
        run_pytest_with_proxy = dedent(
            f"""
        {run_proxy} &
        proxy_pid=$!
        {command}
        pytest_exit=$?
        kill $proxy_pid
        wait $proxy_pid
        exit $pytest_exit
        """
        )
        return ["bash", "-c", f"'{run_pytest_with_proxy}'"]

    def __init__(self, context: ConnectorContext) -> None:
        """Create a step to run live tests for a connector.

        Args:
            context (ConnectorContext): The current test context, providing a connector object, a dagger client and a repository directory.
        """
        super().__init__(context)
        self.connector_image = context.docker_image.split(":")[0]
        options = self.context.run_step_options.step_params.get(CONNECTOR_TEST_STEP_ID.CONNECTOR_LIVE_TESTS, {})

        self.test_suite = self.context.run_step_options.get_item_or_default(options, "test-suite", LiveTestSuite.REGRESSION.value)
        self.connection_id = self._get_connection_id(options)
        self.pr_url = self._get_pr_url(options)

        self.test_dir = self.test_suite_to_dir[LiveTestSuite(self.test_suite)]
        self.control_version = self.context.run_step_options.get_item_or_default(options, "control-version", None)
        self.target_version = self.context.run_step_options.get_item_or_default(options, "target-version", "dev")
        self.should_read_with_state = "should-read-with-state" in options
        self.disable_proxy = "disable-proxy" in options
        self.selected_streams = self.context.run_step_options.get_item_or_default(options, "selected-streams", None)
        self.test_evaluation_mode = "strict" if self.context.connector.metadata.get("supportLevel") == "certified" else "diagnostic"
        self.connection_subset = self.context.run_step_options.get_item_or_default(options, "connection-subset", "sandboxes")
        self.run_id = os.getenv("GITHUB_RUN_ID") or str(int(time.time()))

    def _get_connection_id(self, options: Dict[str, List[Any]]) -> Optional[str]:
        if self.context.is_pr:
            connection_id = self._get_connection_from_test_connections()
            self.logger.info(
                f"Context is {self.context.ci_context}; got connection_id={connection_id} from metadata.yaml liveTests testConnections."
            )
        else:
            connection_id = self.context.run_step_options.get_item_or_default(options, "connection-id", None)
            self.logger.info(f"Context is {self.context.ci_context}; got connection_id={connection_id} from input options.")
        return connection_id

    def _get_pr_url(self, options: Dict[str, List[Any]]) -> Optional[str]:
        if self.context.is_pr:
            pull_request = self.context.pull_request.url if self.context.pull_request else None
            self.logger.info(f"Context is {self.context.ci_context}; got pull_request={pull_request} from context.")
        else:
            pull_request = self.context.run_step_options.get_item_or_default(options, "pr-url", None)
            self.logger.info(f"Context is {self.context.ci_context}; got pull_request={pull_request} from input options.")
        return pull_request

    def _validate_job_can_run(self) -> None:
        connector_type = self.context.connector.metadata.get("connectorType")
        connector_subtype = self.context.connector.metadata.get("connectorSubtype")
        assert connector_type == "source", f"Live tests can only run against source connectors, got `connectorType={connector_type}`."
        if connector_subtype == "database":
            assert (
                self.connection_subset == "sandboxes"
            ), f"Live tests for database sources may only be run against sandbox connections, got `connection_subset={self.connection_subset}`."

        assert self.connection_id, "`connection-id` is required to run live tests."
        assert self.pr_url, "`pr_url` is required to run live tests."

        if self.context.is_pr:
            connection_id_is_valid = False
            for test_suite in self.context.connector.metadata.get("connectorTestSuitesOptions", []):
                if test_suite["suite"] == "liveTests":
                    assert self.connection_id in [
                        option["id"] for option in test_suite.get("testConnections", [])
                    ], f"Connection ID {self.connection_id} was not in the list of valid test connections."
                    connection_id_is_valid = True
                    break
            assert connection_id_is_valid, f"Connection ID {self.connection_id} is not a valid sandbox connection ID."

    def _get_connection_from_test_connections(self) -> Optional[str]:
        for test_suite in self.context.connector.metadata.get("connectorTestSuitesOptions", []):
            if test_suite["suite"] == "liveTests":
                for option in test_suite.get("testConnections", []):
                    connection_id = option["id"]
                    connection_name = option["name"]
                    self.logger.info(f"Using connection name={connection_name}; id={connection_id}")
                    return connection_id
        return None

    async def _run(self, connector_under_test_container: Container) -> StepResult:
        """Run the regression test suite.

        Args:
            connector_under_test (Container): The container holding the target connector test image.

        Returns:
            StepResult: Failure or success of the regression tests with stdout and stderr.
        """
        try:
            self._validate_job_can_run()
        except AssertionError as exc:
            self.logger.info(f"Skipping live tests for {self.context.connector.technical_name} due to validation error {str(exc)}.")
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                exc_info=exc,
            )

        container = await self._build_test_container(await connector_under_test_container.id())
        command = self._run_command_with_proxy(" ".join(self._test_command()))
        main_logger.info(f"Running command {command}")
        container = container.with_(hacks.never_fail_exec(command))
        tests_artifacts_dir = str(self.local_tests_artifacts_dir)
        path_to_report = f"{tests_artifacts_dir}/session_{self.run_id}/report.html"

        exit_code, stdout, stderr = await get_exec_result(container)

        try:
            if (
                f"session_{self.run_id}" not in await container.directory(f"{tests_artifacts_dir}").entries()
                or "report.html" not in await container.directory(f"{tests_artifacts_dir}/session_{self.run_id}").entries()
            ):
                main_logger.exception(
                    "The report file was not generated, an unhandled error likely happened during regression test execution, please check the step stderr and stdout for more details"
                )
                regression_test_report = None
            else:
                await container.file(path_to_report).export(path_to_report)
                with open(path_to_report, "r") as fp:
                    regression_test_report = fp.read()
        except dagger.QueryError as exc:
            regression_test_report = None
            main_logger.exception(
                "The test artifacts directory was not generated, an unhandled error likely happened during setup, please check the step stderr and stdout for more details",
                exc_info=exc,
            )

        return StepResult(
            step=self,
            status=self.get_step_status_from_exit_code(exit_code),
            stderr=stderr,
            stdout=stdout,
            output=container,
            report=regression_test_report,
            consider_in_overall_status=False if self.context.is_pr else True,
        )

    async def _build_test_container(self, target_container_id: str) -> Container:
        """Create a container to run regression tests."""
        container = with_poetry(self.context)
        container_requirements = ["apt-get", "install", "-y", "git", "curl", "docker.io"]
        if not self.context.is_ci:
            # Outside of CI we use ssh to get the connection-retriever package from airbyte-platform-internal
            container_requirements += ["openssh-client"]
        container = (
            container.with_exec(["apt-get", "update"], use_entrypoint=True)
            .with_exec(container_requirements)
            .with_exec(["bash", "-c", "curl https://sdk.cloud.google.com | bash"], use_entrypoint=True)
            .with_env_variable("PATH", "/root/google-cloud-sdk/bin:$PATH", expand=True)
            .with_mounted_directory("/app", self.context.live_tests_dir)
            .with_workdir("/app")
            # Enable dagger-in-dagger
            .with_unix_socket("/var/run/docker.sock", self.dagger_client.host().unix_socket("/var/run/docker.sock"))
            .with_env_variable("RUN_IN_AIRBYTE_CI", "1")
            .with_file(
                "/tmp/record_obfuscator.py",
                self.context.get_repo_dir("tools/bin", include=["record_obfuscator.py"]).file("record_obfuscator.py"),
            )
            # The connector being tested is already built and is stored in a location accessible to an inner dagger kicked off by
            # regression tests. The connector can be found if you know the container ID, so we write the container ID to a file and put
            # it in the regression test container. This way regression tests will use the already-built connector instead of trying to
            # build their own.
            .with_new_file(
                f"/tmp/{slugify(self.connector_image + ':' + self.target_version)}_container_id.txt", contents=str(target_container_id)
            )
        )

        if self.context.is_ci:
            container = (
                container.with_exec(
                    [
                        "sed",
                        "-i",
                        "-E",
                        rf"s,git@github\.com:{self.platform_repo_url},https://github.com/{self.platform_repo_url}.git,",
                        "pyproject.toml",
                    ],
                    use_entrypoint=True,
                )
                .with_exec(
                    [
                        "poetry",
                        "source",
                        "add",
                        "--priority=supplemental",
                        "airbyte-platform-internal-source",
                        "https://github.com/airbytehq/airbyte-platform-internal.git",
                    ],
                    use_entrypoint=True,
                )
                .with_secret_variable(
                    "CI_GITHUB_ACCESS_TOKEN",
                    self.context.dagger_client.set_secret(
                        "CI_GITHUB_ACCESS_TOKEN", self.context.ci_github_access_token.value if self.context.ci_github_access_token else ""
                    ),
                )
                .with_exec(
                    [
                        "/bin/sh",
                        "-c",
                        f"poetry config http-basic.airbyte-platform-internal-source {self.github_user} $CI_GITHUB_ACCESS_TOKEN",
                    ],
                    use_entrypoint=True,
                )
                # Add GCP credentials from the environment and point google to their location (also required for connection-retriever)
                .with_new_file("/tmp/credentials.json", contents=os.getenv("GCP_INTEGRATION_TESTER_CREDENTIALS", ""))
                .with_env_variable("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/credentials.json")
                .with_exec(
                    [
                        "curl",
                        "-o",
                        "cloud-sql-proxy",
                        "https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.0/cloud-sql-proxy.linux.amd64",
                    ],
                    use_entrypoint=True,
                )
                .with_exec(["chmod", "+x", "cloud-sql-proxy"], use_entrypoint=True)
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

        container = container.with_exec(["poetry", "lock"], use_entrypoint=True).with_exec(["poetry", "install"], use_entrypoint=True)
        return container
