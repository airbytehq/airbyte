#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module declaring context related classes."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from functools import lru_cache
from glob import glob
from types import TracebackType
from typing import TYPE_CHECKING, Dict

from asyncer import asyncify
from dagger import Client, Directory, File, GitRepository
from dagger import Secret as DaggerSecret
from dagger import Service
from github import PullRequest
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.consts import CIContext, ContextState
from pipelines.helpers.execution.run_steps import RunStepOptions
from pipelines.helpers.github import update_commit_status_check
from pipelines.helpers.slack import send_message_to_webhook
from pipelines.helpers.utils import AIRBYTE_REPO_URL, java_log_scrub_pattern
from pipelines.models.reports import Report
from pipelines.models.secrets import Secret, SecretStore

if TYPE_CHECKING:
    from typing import List, Optional


class PipelineContext:
    """The pipeline context is used to store configuration for a specific pipeline run."""

    _dagger_client: Optional[Client]
    _report: Optional[Report | ConnectorReport]
    dockerd_service: Optional[Service]
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]

    secrets_to_mask: List[str]

    PRODUCTION = bool(os.environ.get("PRODUCTION", False))  # Set this to True to enable production mode (e.g. to send PR comments)

    @lru_cache
    def get_default_excluded_files(self) -> list[str]:
        return (
            [".git", "airbyte-ci/connectors/pipelines/*"]
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
            + glob("**/.gradle", recursive=True)
        )

    def __init__(
        self,
        pipeline_name: str,
        is_local: bool,
        git_branch: str,
        git_revision: str,
        diffed_branch: str,
        git_repo_url: str,
        report_output_prefix: str,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        is_ci_optional: bool = False,
        slack_webhook: Optional[str] = None,
        reporting_slack_channel: Optional[str] = None,
        pull_request: Optional[PullRequest.PullRequest] = None,
        ci_report_bucket: Optional[str] = None,
        ci_gcp_credentials: Optional[Secret] = None,
        ci_git_user: Optional[str] = None,
        ci_github_access_token: Optional[Secret] = None,
        run_step_options: RunStepOptions = RunStepOptions(),
        enable_report_auto_open: bool = True,
        secret_stores: Dict[str, SecretStore] | None = None,
    ) -> None:
        """Initialize a pipeline context.

        Args:
            pipeline_name (str): The pipeline name.
            is_local (bool): Whether the context is for a local run or a CI run.
            git_branch (str): The current git branch name.
            git_revision (str): The current git revision, commit hash.
            diffed_branch (str): The branch to diff against.
            git_repo_url (str): The git repository URL.
            report_output_prefix (str): The prefix to use for the report output.
            gha_workflow_run_url (Optional[str], optional): URL to the github action workflow run. Only valid for CI run. Defaults to None.
            dagger_logs_url (Optional[str], optional): URL to the dagger logs. Only valid for CI run. Defaults to None.
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
        self.diffed_branch = diffed_branch
        self.git_repo_url = git_repo_url
        self.report_output_prefix = report_output_prefix
        self.gha_workflow_run_url = gha_workflow_run_url
        self.dagger_logs_url = dagger_logs_url
        self.pipeline_start_timestamp = pipeline_start_timestamp
        self.created_at = datetime.utcnow()
        self.ci_context = ci_context
        self.state = ContextState.INITIALIZED
        self.is_ci_optional = is_ci_optional
        self.slack_webhook = slack_webhook
        self.reporting_slack_channel = reporting_slack_channel
        self.pull_request = pull_request
        self.logger = logging.getLogger(self.pipeline_name)
        self._dagger_client = None
        self._report = None
        self.dockerd_service = None
        self.ci_gcp_credentials = ci_gcp_credentials
        self.ci_report_bucket = ci_report_bucket
        self.ci_git_user = ci_git_user
        self.ci_github_access_token = ci_github_access_token
        self.started_at = None
        self.stopped_at = None
        self.secrets_to_mask = []
        self.run_step_options = run_step_options
        self.enable_report_auto_open = enable_report_auto_open
        self.secret_stores = secret_stores if secret_stores else {}
        update_commit_status_check(**self.github_commit_status)

    @property
    def dagger_client(self) -> Client:
        assert self._dagger_client is not None, "The dagger client was not set on this PipelineContext"
        return self._dagger_client

    @dagger_client.setter
    def dagger_client(self, dagger_client: Client) -> None:
        self._dagger_client = dagger_client

    @property
    def is_ci(self) -> bool:
        return self.is_local is False

    @property
    def is_pr(self) -> bool:
        return self.ci_context == CIContext.PULL_REQUEST

    @property
    def repo(self) -> GitRepository:
        return self.dagger_client.git(AIRBYTE_REPO_URL, keep_git_dir=True)

    @property
    def report(self) -> Report | ConnectorReport | None:
        return self._report

    @report.setter
    def report(self, report: Report | ConnectorReport) -> None:
        self._report = report

    @property
    def java_log_scrub_pattern_secret(self) -> Optional[DaggerSecret]:
        if not self.secrets_to_mask:
            return None
        return self.dagger_client.set_secret("log_scrub_pattern", java_log_scrub_pattern(self.secrets_to_mask))

    @property
    def github_commit_status(self) -> dict:
        """Build a dictionary used as kwargs to the update_commit_status_check function."""
        target_url: Optional[str] = self.gha_workflow_run_url

        if (
            self.remote_storage_enabled
            and self.state not in [ContextState.RUNNING, ContextState.INITIALIZED]
            and isinstance(self.report, ConnectorReport)
        ):
            target_url = self.report.html_report_url

        return {
            "sha": self.git_revision,
            "state": self.state.value["github_state"],
            "target_url": target_url,
            "description": self.state.value["description"],
            "context": self.pipeline_name,
            "should_send": self.is_pr,
            "logger": self.logger,
            "is_optional": self.is_ci_optional,
        }

    @property
    def should_send_slack_message(self) -> bool:
        return self.slack_webhook is not None and self.reporting_slack_channel is not None

    @property
    def has_dagger_cloud_token(self) -> bool:
        return "_EXPERIMENTAL_DAGGER_CLOUD_TOKEN" in os.environ

    @property
    def dagger_cloud_url(self) -> Optional[str]:
        """Gets the link to the Dagger Cloud runs page for the current commit."""
        if self.is_local or not self.has_dagger_cloud_token:
            return None

        return f"https://alpha.dagger.cloud/changeByPipelines?filter=dagger.io/git.ref:{self.git_revision}"

    @property
    def remote_storage_enabled(self) -> bool:
        return self.is_ci and bool(self.ci_report_bucket) and bool(self.ci_gcp_credentials)

    def get_repo_file(self, file_path: str) -> File:
        """Get a file from the current repository.

        The file is extracted from the host file system.

        Args:
            file_path (str): Path to the file to get.

        Returns:
            Path: The selected repo file.
        """
        return self.dagger_client.host().file(file_path)

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
            exclude = self.get_default_excluded_files()
        else:
            exclude += self.get_default_excluded_files()
            exclude = list(set(exclude))
        exclude.sort()  # sort to make sure the order is always the same to not burst the cache. Casting exclude to set can change the order
        if subdir != ".":
            subdir = f"{subdir}/" if not subdir.endswith("/") else subdir
            exclude = [f.replace(subdir, "") for f in exclude if subdir in f]
        return self.dagger_client.host().directory(subdir, exclude=exclude, include=include)

    def create_slack_message(self) -> str:
        raise NotImplementedError()

    async def __aenter__(self) -> PipelineContext:
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
        self.logger.info("Caching the latest CDK version...")
        await asyncify(update_commit_status_check)(**self.github_commit_status)
        if self.should_send_slack_message:
            # Using a type ignore here because the should_send_slack_message property is checking for non nullity of the slack_webhook and reporting_slack_channel
            await asyncify(send_message_to_webhook)(
                self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook  # type: ignore
            )
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
        if exception_value:
            self.logger.error("An error was handled by the Pipeline", exc_info=True)

        if self.report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.report = Report(self, steps_results=[])

        self.state = self.determine_final_state(self.report, exception_value)
        self.stopped_at = datetime.utcnow()

        self.report.print()

        await asyncify(update_commit_status_check)(**self.github_commit_status)
        if self.should_send_slack_message:
            # Using a type ignore here because the should_send_slack_message property is checking for non nullity of the slack_webhook and reporting_slack_channel
            await asyncify(send_message_to_webhook)(
                self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook  # type: ignore
            )
        # supress the exception if it was handled
        return True
