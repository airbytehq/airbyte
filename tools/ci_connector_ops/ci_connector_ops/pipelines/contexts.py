#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module declaring context related classes."""

import logging
import os
from datetime import datetime
from enum import Enum
from glob import glob
from types import TracebackType
from typing import List, Optional

import yaml
from anyio import Path
from asyncer import asyncify
from ci_connector_ops.pipelines.actions import secrets
from ci_connector_ops.pipelines.bases import CIContext, ConnectorReport, Report
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.slack import send_message_to_webhook
from ci_connector_ops.pipelines.utils import AIRBYTE_REPO_URL, METADATA_FILE_NAME, sanitize_gcs_credentials
from ci_connector_ops.utils import Connector
from dagger import Client, Directory, Secret
from github import PullRequest


class ContextState(Enum):
    """Enum to characterize the current context state, values are used for external representation on GitHub commit checks."""

    INITIALIZED = {"github_state": "pending", "description": "Pipelines are being initialized..."}
    RUNNING = {"github_state": "pending", "description": "Pipelines are running..."}
    ERROR = {"github_state": "error", "description": "Something went wrong while running the Pipelines."}
    SUCCESSFUL = {"github_state": "success", "description": "All Pipelines ran successfully."}
    FAILURE = {"github_state": "failure", "description": "Pipeline failed."}


class PipelineContext:
    """The pipeline context is used to store configuration for a specific pipeline run."""

    PRODUCTION = bool(os.environ.get("PRODUCTION", False))  # Set this to True to enable production mode (e.g. to send PR comments)

    DEFAULT_EXCLUDED_FILES = (
        [".git"]
        + glob("**/build", recursive=True)
        + glob("**/.venv", recursive=True)
        + glob("**/secrets", recursive=True)
        + glob("**/__pycache__", recursive=True)
        + glob("**/*.egg-info", recursive=True)
        + glob("**/.vscode", recursive=True)
        + glob("**/.pytest_cache", recursive=True)
        + glob("**/.eggs", recursive=True)
        + glob("**/.mypy_cache", recursive=True)
        + glob("**/.DS_Store", recursive=True)
        + glob("**/airbyte_ci_logs", recursive=True)
    )

    def __init__(
        self,
        pipeline_name: str,
        is_local: bool,
        git_branch: str,
        git_revision: str,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        is_ci_optional: bool = False,
        slack_webhook: Optional[str] = None,
        reporting_slack_channel: Optional[str] = None,
        pull_request: PullRequest = None,
        ci_report_bucket: Optional[str] = None,
        ci_gcs_credentials: Optional[str] = None,
        ci_git_user: Optional[str] = None,
        ci_github_access_token: Optional[str] = None,
    ):
        """Initialize a pipeline context.

        Args:
            pipeline_name (str): The pipeline name.
            is_local (bool): Whether the context is for a local run or a CI run.
            git_branch (str): The current git branch name.
            git_revision (str): The current git revision, commit hash.
            gha_workflow_run_url (Optional[str], optional): URL to the github action workflow run. Only valid for CI run. Defaults to None.
            pipeline_start_timestamp (Optional[int], optional): Timestamp at which the pipeline started. Defaults to None.
            ci_context (Optional[str], optional): Pull requests, workflow dispatch or nightly build. Defaults to None.
            is_ci_optional (bool, optional): Whether the CI is optional. Defaults to False.
            slack_webhook (Optional[str], optional): Slack webhook to send messages to. Defaults to None.
            reporting_slack_channel (Optional[str], optional): Slack channel to send messages to. Defaults to None.
            pull_request (PullRequest, optional): The pull request object if the pipeline was triggered by a pull request. Defaults to None.
        """
        self.pipeline_name = pipeline_name
        self.is_local = is_local
        self.git_branch = git_branch
        self.git_revision = git_revision
        self.gha_workflow_run_url = gha_workflow_run_url
        self.pipeline_start_timestamp = pipeline_start_timestamp
        self.created_at = datetime.utcnow()
        self.ci_context = ci_context
        self.state = ContextState.INITIALIZED
        self.is_ci_optional = is_ci_optional
        self.slack_webhook = slack_webhook
        self.reporting_slack_channel = reporting_slack_channel
        self.pull_request = pull_request
        self.logger = logging.getLogger(self.pipeline_name)
        self.dagger_client = None
        self._report = None
        self.dockerd_service = None
        self.ci_gcs_credentials = sanitize_gcs_credentials(ci_gcs_credentials) if ci_gcs_credentials else None
        self.ci_report_bucket = ci_report_bucket
        self.ci_git_user = ci_git_user
        self.ci_github_access_token = ci_github_access_token
        self.started_at = None
        self.stopped_at = None
        update_commit_status_check(**self.github_commit_status)

    @property
    def dagger_client(self) -> Client:  # noqa D102
        return self._dagger_client

    @dagger_client.setter
    def dagger_client(self, dagger_client: Client):  # noqa D102
        self._dagger_client = dagger_client

    @property
    def is_ci(self):  # noqa D102
        return self.is_local is False

    @property
    def is_pr(self):  # noqa D102
        return self.ci_context == CIContext.PULL_REQUEST

    @property
    def repo(self):  # noqa D102
        return self.dagger_client.git(AIRBYTE_REPO_URL, keep_git_dir=True)

    @property
    def report(self) -> Report:  # noqa D102
        return self._report

    @report.setter
    def report(self, report: Report):  # noqa D102
        self._report = report

    @property
    def ci_gcs_credentials_secret(self) -> Secret:
        return self.dagger_client.set_secret("ci_gcs_credentials", self.ci_gcs_credentials)

    @property
    def ci_github_access_token_secret(self) -> Secret:
        return self.dagger_client.set_secret("ci_github_access_token", self.ci_github_access_token)

    @property
    def github_commit_status(self) -> dict:
        """Build a dictionary used as kwargs to the update_commit_status_check function."""
        return {
            "sha": self.git_revision,
            "state": self.state.value["github_state"],
            "target_url": self.gha_workflow_run_url,
            "description": self.state.value["description"],
            "context": self.pipeline_name,
            "should_send": self.is_pr,
            "logger": self.logger,
            "is_optional": self.is_ci_optional,
        }

    @property
    def should_send_slack_message(self) -> bool:
        return self.slack_webhook is not None and self.reporting_slack_channel is not None

    def get_repo_dir(self, subdir: str = ".", exclude: Optional[List[str]] = None, include: Optional[List[str]] = None) -> Directory:
        """Get a directory from the current repository.

        The directory is extracted from the host file system.
        A couple of files or directories that could corrupt builds are exclude by default (check DEFAULT_EXCLUDED_FILES).

        Args:
            subdir (str, optional): Path to the subdirectory to get. Defaults to "." to get the full repository.
            exclude ([List[str], optional): List of files or directories to exclude from the directory. Defaults to None.
            include ([List[str], optional): List of files or directories to include in the directory. Defaults to None.

        Returns:
            Directory: The selected repo directory.
        """
        if exclude is None:
            exclude = self.DEFAULT_EXCLUDED_FILES
        else:
            exclude += self.DEFAULT_EXCLUDED_FILES
            exclude = list(set(exclude))
        if subdir != ".":
            subdir = f"{subdir}/" if not subdir.endswith("/") else subdir
            exclude = [f.replace(subdir, "") for f in exclude if subdir in f]
        return self.dagger_client.host().directory(subdir, exclude=exclude, include=include)

    def create_slack_message(self) -> str:
        raise NotImplementedError()

    async def __aenter__(self):
        """Perform setup operation for the PipelineContext.

        Updates the current commit status on Github.

        Raises:
            Exception: An error is raised when the context was not initialized with a Dagger client
        Returns:
            PipelineContext: A running instance of the PipelineContext.
        """
        if self.dagger_client is None:
            raise Exception("A Pipeline can't be entered with an undefined dagger_client")
        self.state = ContextState.RUNNING
        self.started_at = datetime.utcnow()
        await asyncify(update_commit_status_check)(**self.github_commit_status)
        if self.should_send_slack_message:
            await asyncify(send_message_to_webhook)(self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook)
        return self

    @staticmethod
    def determine_final_state(report: Optional[Report], exception_value: Optional[BaseException]) -> ContextState:
        """Determine the final state of the context from the report or the exception value.

        Args:
            report (Optional[Report]): The pipeline report if any.
            exception_value (Optional[BaseException]): The exception value if an exception was raised in the context execution, None otherwise.
        Returns:
            ContextState: The final state of the context.
        """
        if exception_value is not None or report is None:
            return ContextState.ERROR
        if report is not None and report.failed_steps:
            return ContextState.FAILURE
        if report is not None and report.success:
            return ContextState.SUCCESSFUL
        raise Exception(
            f"The final state of the context could not be determined for the report and exception value provided. Report: {report}, Exception: {exception_value}"
        )

    async def __aexit__(
        self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> bool:
        """Perform teardown operation for the PipelineContext.

        On the context exit the following operations will happen:
            - Log the error value if an error was handled.
            - Log the test report.
            - Update the commit status check on GitHub if running in a CI environment.

        It should gracefully handle all the execution errors that happened and always upload a test report and update commit status check.

        Args:
            exception_type (Optional[type[BaseException]]): The exception type if an exception was raised in the context execution, None otherwise.
            exception_value (Optional[BaseException]): The exception value if an exception was raised in the context execution, None otherwise.
            traceback (Optional[TracebackType]): The traceback if an exception was raised in the context execution, None otherwise.
        Returns:
            bool: Whether the teardown operation ran successfully.
        """
        self.state = self.determine_final_state(self.report, exception_value)
        self.stopped_at = datetime.utcnow()

        if exception_value:
            self.logger.error("An error was handled by the Pipeline", exc_info=True)
        if self.report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.report = Report(self, steps_results=[])

        self.report.print()
        self.logger.info(self.report.to_json())

        await asyncify(update_commit_status_check)(**self.github_commit_status)
        if self.should_send_slack_message:
            await asyncify(send_message_to_webhook)(self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook)
        # supress the exception if it was handled
        return True


class ConnectorContext(PipelineContext):
    """The connector context is used to store configuration for a specific connector pipeline run."""

    DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE = "airbyte/connector-acceptance-test:latest"

    def __init__(
        self,
        pipeline_name: str,
        connector: Connector,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        modified_files: List[str],
        report_output_prefix: str,
        use_remote_secrets: bool = True,
        ci_report_bucket: Optional[str] = None,
        ci_gcs_credentials: Optional[str] = None,
        ci_git_user: Optional[str] = None,
        ci_github_access_token: Optional[str] = None,
        connector_acceptance_test_image: Optional[str] = DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        reporting_slack_channel: Optional[str] = None,
        pull_request: PullRequest = None,
    ):
        """Initialize a connector context.

        Args:
            connector (Connector): The connector under test.
            is_local (bool): Whether the context is for a local run or a CI run.
            git_branch (str): The current git branch name.
            git_revision (str): The current git revision, commit hash.
            modified_files (List[str]): The list of modified files in the current git branch.
            report_output_prefix (str): The S3 key to upload the test report to.
            use_remote_secrets (bool, optional): Whether to download secrets for GSM or use the local secrets. Defaults to True.
            connector_acceptance_test_image (Optional[str], optional): The image to use to run connector acceptance tests. Defaults to DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE.
            gha_workflow_run_url (Optional[str], optional): URL to the github action workflow run. Only valid for CI run. Defaults to None.
            pipeline_start_timestamp (Optional[int], optional): Timestamp at which the pipeline started. Defaults to None.
            ci_context (Optional[str], optional): Pull requests, workflow dispatch or nightly build. Defaults to None.
            slack_webhook (Optional[str], optional): The slack webhook to send messages to. Defaults to None.
            reporting_slack_channel (Optional[str], optional): The slack channel to send messages to. Defaults to None.
            pull_request (PullRequest, optional): The pull request object if the pipeline was triggered by a pull request. Defaults to None.
        """

        self.pipeline_name = pipeline_name
        self.connector = connector
        self.use_remote_secrets = use_remote_secrets
        self.connector_acceptance_test_image = connector_acceptance_test_image
        self.modified_files = modified_files
        self.report_output_prefix = report_output_prefix
        self._secrets_dir = None
        self._updated_secrets_dir = None
        self.cdk_version = None

        super().__init__(
            pipeline_name=pipeline_name,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            slack_webhook=slack_webhook,
            reporting_slack_channel=reporting_slack_channel,
            pull_request=pull_request,
            ci_report_bucket=ci_report_bucket,
            ci_gcs_credentials=ci_gcs_credentials,
            ci_git_user=ci_git_user,
            ci_github_access_token=ci_github_access_token,
        )

    @property
    def secrets_dir(self) -> Directory:  # noqa D102
        return self._secrets_dir

    @secrets_dir.setter
    def secrets_dir(self, secrets_dir: Directory):  # noqa D102
        self._secrets_dir = secrets_dir

    @property
    def updated_secrets_dir(self) -> Directory:  # noqa D102
        return self._updated_secrets_dir

    @updated_secrets_dir.setter
    def updated_secrets_dir(self, updated_secrets_dir: Directory):  # noqa D102
        self._updated_secrets_dir = updated_secrets_dir

    @property
    def connector_acceptance_test_source_dir(self) -> Directory:  # noqa D102
        return self.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")

    @property
    def should_save_updated_secrets(self) -> bool:  # noqa D102
        return self.use_remote_secrets and self.updated_secrets_dir is not None

    @property
    def host_image_export_dir_path(self) -> str:
        return "." if self.is_ci else "/tmp"

    @property
    def metadata_path(self) -> Path:
        return self.connector.code_directory / METADATA_FILE_NAME

    @property
    def metadata(self) -> dict:
        return yaml.safe_load(self.metadata_path.read_text())["data"]

    @property
    def docker_image_from_metadata(self) -> str:
        return f"{self.metadata['dockerRepository']}:{self.metadata['dockerImageTag']}"

    def get_connector_dir(self, exclude=None, include=None) -> Directory:
        """Get the connector under test source code directory.

        Args:
            exclude ([List[str], optional): List of files or directories to exclude from the directory. Defaults to None.
            include ([List[str], optional): List of files or directories to include in the directory. Defaults to None.

        Returns:
            Directory: The connector under test source code directory.
        """
        return self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)

    async def __aexit__(
        self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> bool:
        """Perform teardown operation for the ConnectorContext.

        On the context exit the following operations will happen:
            - Upload updated connector secrets back to Google Secret Manager
            - Write a test report in JSON format locally and to S3 if running in a CI environment
            - Update the commit status check on GitHub if running in a CI environment.
        It should gracefully handle the execution error that happens and always upload a test report and update commit status check.
        Args:
            exception_type (Optional[type[BaseException]]): The exception type if an exception was raised in the context execution, None otherwise.
            exception_value (Optional[BaseException]): The exception value if an exception was raised in the context execution, None otherwise.
            traceback (Optional[TracebackType]): The traceback if an exception was raised in the context execution, None otherwise.
        Returns:
            bool: Whether the teardown operation ran successfully.
        """
        self.stopped_at = datetime.utcnow()
        self.state = self.determine_final_state(self.report, exception_value)
        if exception_value:
            self.logger.error("An error got handled by the ConnectorContext", exc_info=True)
        if self.report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.report = ConnectorReport(self, [])

        if self.should_save_updated_secrets:
            await secrets.upload(self)

        self.report.print()
        self.logger.info(self.report.to_json())

        await self.report.save()

        if self.report.should_be_commented_on_pr:
            self.report.post_comment_on_pr()

        await asyncify(update_commit_status_check)(**self.github_commit_status)

        if self.should_send_slack_message:
            await asyncify(send_message_to_webhook)(self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook)

        # Supress the exception if any
        return True

    def create_slack_message(self) -> str:
        raise NotImplementedError


class PublishConnectorContext(ConnectorContext):
    def __init__(
        self,
        connector: Connector,
        pre_release: bool,
        modified_files: List[str],
        spec_cache_gcs_credentials: str,
        spec_cache_bucket_name: str,
        metadata_service_gcs_credentials: str,
        metadata_bucket_name: str,
        docker_hub_username: str,
        docker_hub_password: str,
        slack_webhook: str,
        reporting_slack_channel: str,
        ci_report_bucket: str,
        report_output_prefix: str,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        ci_gcs_credentials: str = None,
        pull_request: PullRequest = None,
    ):
        self.pre_release = pre_release
        self.spec_cache_bucket_name = spec_cache_bucket_name
        self.metadata_bucket_name = metadata_bucket_name
        self.spec_cache_gcs_credentials = sanitize_gcs_credentials(spec_cache_gcs_credentials)
        self.metadata_service_gcs_credentials = sanitize_gcs_credentials(metadata_service_gcs_credentials)
        self.docker_hub_username = docker_hub_username
        self.docker_hub_password = docker_hub_password

        pipeline_name = f"Publish {connector.technical_name}"
        pipeline_name = pipeline_name + " (pre-release)" if pre_release else pipeline_name

        super().__init__(
            pipeline_name=pipeline_name,
            connector=connector,
            modified_files=modified_files,
            report_output_prefix=report_output_prefix,
            ci_report_bucket=ci_report_bucket,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            slack_webhook=slack_webhook,
            reporting_slack_channel=reporting_slack_channel,
            ci_gcs_credentials=ci_gcs_credentials,
        )

    @property
    def docker_hub_username_secret(self) -> Secret:
        return self.dagger_client.set_secret("docker_hub_username", self.docker_hub_username)

    @property
    def docker_hub_password_secret(self) -> Secret:
        return self.dagger_client.set_secret("docker_hub_password", self.docker_hub_password)

    @property
    def metadata_service_gcs_credentials_secret(self) -> Secret:
        return self.dagger_client.set_secret("metadata_service_gcs_credentials", self.metadata_service_gcs_credentials)

    @property
    def spec_cache_gcs_credentials_secret(self) -> Secret:
        return self.dagger_client.set_secret("spec_cache_gcs_credentials", self.spec_cache_gcs_credentials)

    @property
    def docker_image_name(self):
        if self.pre_release:
            return f"{self.docker_image_from_metadata}-dev.{self.git_revision[:10]}"
        else:
            return self.docker_image_from_metadata

    def create_slack_message(self) -> str:
        docker_hub_url = f"https://hub.docker.com/r/{self.connector.metadata['dockerRepository']}/tags"
        message = f"*Publish <{docker_hub_url}|{self.docker_image_name}>*\n"
        if self.is_ci:
            message += f"🤖 <{self.gha_workflow_run_url}|GitHub Action workflow>\n"
        else:
            message += "🧑‍💻 Local run\n"
        message += f"*Connector:* {self.connector.technical_name}\n"
        message += f"*Version:* {self.connector.version}\n"
        branch_url = f"https://github.com/airbytehq/airbyte/tree/{self.git_branch}"
        message += f"*Branch:* <{branch_url}|{self.git_branch}>\n"
        commit_url = f"https://github.com/airbytehq/airbyte/commit/{self.git_revision}"
        message += f"*Commit:* <{commit_url}|{self.git_revision[:10]}>\n"
        if self.state in [ContextState.INITIALIZED, ContextState.RUNNING]:
            message += "🟠"
        if self.state is ContextState.SUCCESSFUL:
            message += "🟢"
        if self.state in [ContextState.FAILURE, ContextState.ERROR]:
            message += "🔴"
        message += f" {self.state.value['description']}\n"
        if self.state is ContextState.SUCCESSFUL:
            message += f"⏲️ Run duration: {round(self.report.run_duration)}s\n"
        if self.state is ContextState.FAILURE:
            message += "\ncc. <!channel>"
        return message
