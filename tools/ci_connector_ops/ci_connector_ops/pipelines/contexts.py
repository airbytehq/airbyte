#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import os
from datetime import datetime
from enum import Enum
from types import TracebackType
from typing import Optional

from anyio import Path
from asyncer import asyncify
from dagger import Client, Directory

from ci_connector_ops.pipelines.actions import remote_storage, secrets
from ci_connector_ops.pipelines.bases import ConnectorTestReport, TestReport
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.utils import AIRBYTE_REPO_URL
from ci_connector_ops.utils import Connector


# create an enum for ci context values which can be ["manual", "pull_request", "nightly_builds"]
# and use it in the context class
class CIContext(str, Enum):
    MANUAL = "manual"
    PULL_REQUEST = "pull_request"
    NIGHTLY_BUILDS = "nightly_builds"


class ContextState(Enum):
    INITIALIZED = {"github_state": "pending", "description": "Pipelines are being initialized..."}
    RUNNING = {"github_state": "pending", "description": "Pipelines are running..."}
    ERROR = {"github_state": "error", "description": "Something went wrong while running the Pipelines."}
    SUCCESSFUL = {"github_state": "success", "description": "All Pipelines ran successfully."}
    FAILURE = {"github_state": "failure", "description": "Pipeline failed."}


class PipelineContext:
    def __init__(
        self,
        pipeline_name: str,
        is_local: bool,
        git_branch: str,
        git_revision: str,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
    ):
        self.pipeline_name = pipeline_name
        self.is_local = is_local
        self.git_branch = git_branch
        self.git_revision = git_revision
        self.gha_workflow_run_url = gha_workflow_run_url
        self.pipeline_start_timestamp = pipeline_start_timestamp
        self.created_at = datetime.utcnow()
        self.ci_context = ci_context
        self.state = ContextState.INITIALIZED

        self.logger = logging.getLogger(self.pipeline_name)
        self.dagger_client = None
        self._test_report = None

        update_commit_status_check(**self.github_commit_status)

    @property
    def dagger_client(self) -> Client:
        return self._dagger_client

    @dagger_client.setter
    def dagger_client(self, dagger_client: Client):
        self._dagger_client = dagger_client

    @property
    def is_ci(self):
        return self.is_local is False

    @property
    def is_pr(self):
        return self.ci_context == CIContext.PULL_REQUEST

    @property
    def repo(self):
        return self.dagger_client.git(AIRBYTE_REPO_URL, keep_git_dir=True)

    @property
    def test_report(self) -> TestReport:
        return self._test_report

    @test_report.setter
    def test_report(self, test_report: TestReport):
        self._test_report = test_report
        self.state = ContextState.SUCCESSFUL if test_report.success else ContextState.FAILURE

    def get_repo_dir(self, subdir=".", exclude=None, include=None) -> Directory:
        if self.is_local:
            return self.dagger_client.host().directory(subdir, exclude=exclude, include=include)
        else:
            return self.repo.branch(self.git_branch).tree().directory(subdir)

    @property
    def github_commit_status(self) -> dict:
        return {
            "sha": self.git_revision,
            "state": self.state.value["github_state"],
            "target_url": self.gha_workflow_run_url,
            "description": self.state.value["description"],
            "context": self.pipeline_name,
            "should_send": self.is_pr,
            "logger": self.logger,
        }

    async def __aenter__(self):
        if self.dagger_client is None:
            raise Exception("A Pipeline can't be entered with an undefined dagger_client")
        self.state = ContextState.RUNNING
        await asyncify(update_commit_status_check)(**self.github_commit_status)
        return self

    async def __aexit__(self, exception_type, exception_value, traceback) -> bool:
        if exception_value:
            self.logger.error("An error was handled by the Pipeline", exc_info=True)
            self.state = ContextState.ERROR

        if self.test_report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.state = ContextState.ERROR
            self.test_report = TestReport(self, steps_results=[])

        self.test_report.print()
        self.logger.info(self.test_report.to_json())

        await asyncify(update_commit_status_check)(**self.github_commit_status)

        # supress the exception if it was handled
        return True


class ConnectorTestContext(PipelineContext):
    """The connector test context is used to store configuration for a specific connector pipeline run."""

    DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE = "airbyte/connector-acceptance-test:latest"

    def __init__(
        self,
        connector: Connector,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        use_remote_secrets: bool = True,
        connector_acceptance_test_image: Optional[str] = DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
    ):
        pipeline_name = f"CI test for {connector.technical_name}"

        self.connector = connector
        self.use_remote_secrets = use_remote_secrets
        self.connector_acceptance_test_image = connector_acceptance_test_image

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
        )

    @property
    def secrets_dir(self) -> Directory:
        return self._secrets_dir

    @secrets_dir.setter
    def secrets_dir(self, secrets_dir: Directory):
        self._secrets_dir = secrets_dir

    @property
    def updated_secrets_dir(self) -> Directory:
        return self._updated_secrets_dir

    @updated_secrets_dir.setter
    def updated_secrets_dir(self, updated_secrets_dir: Directory):
        self._updated_secrets_dir = updated_secrets_dir

    @property
    def connector_acceptance_test_source_dir(self) -> Directory:
        return self.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")

    @property
    def should_save_updated_secrets(self):
        return self.use_remote_secrets and self.updated_secrets_dir is not None

    def get_connector_dir(self, exclude=None, include=None) -> Directory:
        return self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)

    async def __aexit__(
        self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> bool:
        """Performs teardown operation for the ConnectorTestContext.
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
            bool: Wether the teardown operation ran successfully.
        """
        if exception_value:
            self.logger.error("An error got handled by the ConnectorTestContext", exc_info=True)
            self.state = ContextState.ERROR
        if self.test_report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.state = ContextState.ERROR
            self.test_report = ConnectorTestReport(self, [])

        self.dagger_client = self.dagger_client.pipeline(f"Teardown {self.connector.technical_name}")
        if self.should_save_updated_secrets:
            await secrets.upload(self)

        self.test_report.print()
        self.logger.info(self.test_report.to_json())

        local_test_reports_path_root = "tools/ci_connector_ops/test_reports/"
        connector_name = self.test_report.pipeline_context.connector.technical_name
        connector_version = self.test_report.pipeline_context.connector.version
        git_revision = self.test_report.pipeline_context.git_revision
        git_branch = self.test_report.pipeline_context.git_branch.replace("/", "_")
        suffix = f"{connector_name}/{git_branch}/{connector_version}/{git_revision}.json"
        local_report_path = Path(local_test_reports_path_root + suffix)
        await local_report_path.parents[0].mkdir(parents=True, exist_ok=True)
        await local_report_path.write_text(self.test_report.to_json())
        if self.test_report.should_be_saved:
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
