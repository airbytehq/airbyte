#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Optional

from anyio import Path
from asyncer import asyncify
from ci_connector_ops.pipelines.actions import remote_storage, secrets
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.models import ConnectorTestReport
from ci_connector_ops.pipelines.utils import AIRBYTE_REPO_URL
from ci_connector_ops.utils import Connector
from dagger import Client, Directory


class ContextState(Enum):
    INITIALIZED = {"github_state": "pending", "description": "Tests are being initialized..."}
    RUNNING = {"github_state": "pending", "description": "Tests are running..."}
    ERROR = {"github_state": "error", "description": "Something went wrong while running the tests."}
    SUCCESSFUL = {"github_state": "success", "description": "All tests ran successfully."}
    FAILURE = {"github_state": "failure", "description": "Test failed."}


class ConnectorTestContext:
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
    ):
        self.connector = connector
        self.is_local = is_local
        self.git_branch = git_branch
        self.git_revision = git_revision
        self.use_remote_secrets = use_remote_secrets
        self.connector_acceptance_test_image = connector_acceptance_test_image
        self.gha_workflow_run_url = gha_workflow_run_url

        self.created_at = datetime.utcnow()

        self.state = ContextState.INITIALIZED
        self.logger = logging.getLogger(self.main_pipeline_name)
        self.dagger_client = None
        self._secrets_dir = None
        self._updated_secrets_dir = None
        self._test_report = None
        update_commit_status_check(**self.github_commit_status)

    @property
    def updated_secrets_dir(self) -> Directory:
        return self._updated_secrets_dir

    @updated_secrets_dir.setter
    def updated_secrets_dir(self, updated_secrets_dir: Directory):
        self._updated_secrets_dir = updated_secrets_dir

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
    def repo(self):
        return self.dagger_client.git(AIRBYTE_REPO_URL, keep_git_dir=True)

    @property
    def connector_acceptance_test_source_dir(self) -> Directory:
        return self.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")

    @property
    def should_save_updated_secrets(self):
        return self.use_remote_secrets and self.updated_secrets_dir is not None

    @property
    def main_pipeline_name(self):
        return f"CI test for {self.connector.technical_name}"

    @property
    def test_report(self) -> ConnectorTestReport:
        return self._test_report

    @test_report.setter
    def test_report(self, test_report: ConnectorTestReport):
        self._test_report = test_report
        self.state = ContextState.SUCCESSFUL if test_report.success else ContextState.FAILURE

    @property
    def github_commit_status(self) -> dict:
        return {
            "sha": self.git_revision,
            "state": self.state.value["github_state"],
            "target_url": self.gha_workflow_run_url,
            "description": self.state.value["description"],
            "context": f"[POC please ignore] Connector tests: {self.connector.technical_name}",
            "should_send": self.is_ci,
            "logger": self.logger,
        }

    def get_repo_dir(self, subdir=".", exclude=None, include=None) -> Directory:
        if self.is_local:
            return self.dagger_client.host().directory(subdir, exclude=exclude, include=include)
        else:
            return self.repo.branch(self.git_branch).tree().directory(subdir)

    def get_connector_dir(self, exclude=None, include=None) -> Directory:
        return self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)

    async def __aenter__(self):
        if self.dagger_client is None:
            raise Exception("A ConnectorTestContext can't be entered with an undefined dagger_client")
        self.secrets_dir = await secrets.get_connector_secret_dir(self)
        self.updated_secrets_dir = None
        self.state = ContextState.RUNNING
        await asyncify(update_commit_status_check)(**self.github_commit_status)
        return self

    async def __aexit__(self, exception_type, exception_value, traceback) -> bool:
        if exception_value:
            self.logger.error("An error got handled by the ConnectorTestContext", exc_info=True)
            self.state = ContextState.ERROR
        elif self.test_report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.state = ContextState.ERROR
            return True
        else:
            teardown_pipeline = self.dagger_client.pipeline(f"Teardown {self.connector.technical_name}")
            if self.should_save_updated_secrets:
                await secrets.upload(
                    teardown_pipeline,
                    self.connector,
                )
            self.test_report.print()
            self.logger.info(self.test_report.to_json())
            local_test_reports_path_root = "tools/ci_connector_ops/test_reports/"
            connector_name = self.test_report.connector_test_context.connector.technical_name
            connector_version = self.test_report.connector_test_context.connector.version
            git_revision = self.test_report.connector_test_context.git_revision
            git_branch = self.test_report.connector_test_context.git_branch.replace("/", "_")
            suffix = f"{connector_name}/{git_branch}/{connector_version}/{git_revision}.json"
            local_report_path = Path(local_test_reports_path_root + suffix)
            await local_report_path.parents[0].mkdir(parents=True, exist_ok=True)
            await local_report_path.write_text(self.test_report.to_json())
            if self.test_report.should_be_saved:
                s3_reports_path_root = "python-poc/tests/history/"
                s3_key = s3_reports_path_root + suffix
                await remote_storage.upload_to_s3(teardown_pipeline, str(local_report_path), s3_key, os.environ["TEST_REPORTS_BUCKET_NAME"])

        await asyncify(update_commit_status_check)(**self.github_commit_status)
        return True
