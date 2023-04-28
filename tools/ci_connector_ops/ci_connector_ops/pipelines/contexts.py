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
from ci_connector_ops.pipelines.actions import remote_storage, secrets
from ci_connector_ops.pipelines.bases import ConnectorReport, Report
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.utils import AIRBYTE_REPO_URL, METADATA_FILE_NAME
from ci_connector_ops.utils import Connector
from dagger import Client, Directory


class CIContext(str, Enum):
    """An enum for Ci context values which can be ["manual", "pull_request", "nightly_builds"]."""

    MANUAL = "manual"
    PULL_REQUEST = "pull_request"
    NIGHTLY_BUILDS = "nightly_builds"
    MASTER = "master"


class ContextState(Enum):
    """Enum to characterize the current context state, values are used for external representation on GitHub commit checks."""

    INITIALIZED = {"github_state": "pending", "description": "Pipelines are being initialized..."}
    RUNNING = {"github_state": "pending", "description": "Pipelines are running..."}
    ERROR = {"github_state": "error", "description": "Something went wrong while running the Pipelines."}
    SUCCESSFUL = {"github_state": "success", "description": "All Pipelines ran successfully."}
    FAILURE = {"github_state": "failure", "description": "Pipeline failed."}


class PipelineContext:
    """The pipeline context is used to store configuration for a specific pipeline run."""

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

        self.logger = logging.getLogger(self.pipeline_name)
        self.dagger_client = None
        self._report = None
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
        self.state = ContextState.SUCCESSFUL if report.success else ContextState.FAILURE

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

    def get_repo_dir(self, subdir: str = ".", exclude: Optional[List[str]] = None, include: Optional[List[str]] = None) -> Directory:
        """Get a directory from the current repository.

        If running in the CI:
        The directory is extracted from the git branch.

        If running locally:
        The directory is extracted from your host file system.
        A couple of files or directories that could corrupt builds are exclude by default (check DEFAULT_EXCLUDED_FILES).

        Args:
            subdir (str, optional): Path to the subdirectory to get. Defaults to "." to get the full repository.
            exclude ([List[str], optional): List of files or directories to exclude from the directory. Defaults to None.
            include ([List[str], optional): List of files or directories to include in the directory. Defaults to None.

        Returns:
            Directory: The selected repo directory.
        """
        if self.is_local:
            if exclude is None:
                exclude = self.DEFAULT_EXCLUDED_FILES
            else:
                exclude += self.DEFAULT_EXCLUDED_FILES
                exclude = list(set(exclude))
            if subdir != ".":
                subdir = f"{subdir}/" if not subdir.endswith("/") else subdir
                exclude = [f.replace(subdir, "") for f in exclude if subdir in f]
            return self.dagger_client.host().directory(subdir, exclude=exclude, include=include)
        else:
            return self.repo.branch(self.git_branch).tree().directory(subdir)

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
        await asyncify(update_commit_status_check)(**self.github_commit_status)
        return self

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
            self.state = ContextState.ERROR

        if self.report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.state = ContextState.ERROR
            self.report = Report(self, steps_results=[])

        self.report.print()
        self.logger.info(self.report.to_json())

        await asyncify(update_commit_status_check)(**self.github_commit_status)

        # supress the exception if it was handled
        return True


class ConnectorContext(PipelineContext):
    """The connector context is used to store configuration for a specific connector pipeline run."""

    DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE = "airbyte/connector-acceptance-test:latest"

    def __init__(
        self,
        connector: Connector,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        modified_files: List[str],
        use_remote_secrets: bool = True,
        connector_acceptance_test_image: Optional[str] = DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
    ):
        """Initialize a connector context.

        Args:
            connector (Connector): The connector under test.
            is_local (bool): Whether the context is for a local run or a CI run.
            git_branch (str): The current git branch name.
            git_revision (str): The current git revision, commit hash.
            use_remote_secrets (bool, optional): Whether to download secrets for GSM or use the local secrets. Defaults to True.
            connector_acceptance_test_image (Optional[str], optional): The image to use to run connector acceptance tests. Defaults to DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE.
            gha_workflow_run_url (Optional[str], optional): URL to the github action workflow run. Only valid for CI run. Defaults to None.
            pipeline_start_timestamp (Optional[int], optional): Timestamp at which the pipeline started. Defaults to None.
            ci_context (Optional[str], optional): Pull requests, workflow dispatch or nightly build. Defaults to None.
        """
        pipeline_name = f"CI test for {connector.technical_name}"

        self.connector = connector
        self.use_remote_secrets = use_remote_secrets
        self.connector_acceptance_test_image = connector_acceptance_test_image
        self.modified_files = modified_files
        self._secrets_dir = None
        self._updated_secrets_dir = None

        super().__init__(
            pipeline_name=pipeline_name,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            # TODO: remove this once stable and our default pipeline
            is_ci_optional=True,
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
        if exception_value:
            self.logger.error("An error got handled by the ConnectorContext", exc_info=True)
            self.state = ContextState.ERROR
        if self.report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.state = ContextState.ERROR
            self.report = ConnectorReport(self, [])

        if self.should_save_updated_secrets:
            await secrets.upload(self)

        self.report.print()
        self.logger.info(self.report.to_json())

        local_reports_path_root = "tools/ci_connector_ops/pipeline_reports/"
        connector_name = self.report.pipeline_context.connector.technical_name
        connector_version = self.report.pipeline_context.connector.version
        git_revision = self.report.pipeline_context.git_revision
        git_branch = self.report.pipeline_context.git_branch.replace("/", "_")
        suffix = f"{connector_name}/{git_branch}/{connector_version}/{git_revision}.json"
        local_report_path = Path(local_reports_path_root + suffix)
        await local_report_path.parents[0].mkdir(parents=True, exist_ok=True)
        await local_report_path.write_text(self.report.to_json())
        if self.report.should_be_saved:
            s3_reports_path_root = "python-poc/tests/history/"
            s3_key = s3_reports_path_root + suffix
            report_upload_exit_code = await remote_storage.upload_to_s3(
                self.dagger_client, str(local_report_path), s3_key, os.environ["TEST_REPORTS_BUCKET_NAME"]
            )
            if report_upload_exit_code != 0:
                self.logger.error("Uploading the report to S3 failed.")
        await asyncify(update_commit_status_check)(**self.github_commit_status)

        # Supress the exception if any
        return True
