#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module declaring context related classes."""

from datetime import datetime
from types import TracebackType
from typing import Optional

import yaml
from anyio import Path
from asyncer import asyncify
from dagger import Directory, Secret
from github import PullRequest
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.dagger.actions import secrets
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from pipelines.helpers.github import update_commit_status_check
from pipelines.helpers.slack import send_message_to_webhook
from pipelines.helpers.utils import METADATA_FILE_NAME
from pipelines.models.contexts.pipeline_context import PipelineContext


class ConnectorContext(PipelineContext):
    """The connector context is used to store configuration for a specific connector pipeline run."""

    DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE = "airbyte/connector-acceptance-test:dev"

    def __init__(
        self,
        pipeline_name: str,
        connector: ConnectorWithModifiedFiles,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        report_output_prefix: str,
        use_remote_secrets: bool = True,
        ci_report_bucket: Optional[str] = None,
        ci_gcs_credentials: Optional[str] = None,
        ci_git_user: Optional[str] = None,
        ci_github_access_token: Optional[str] = None,
        connector_acceptance_test_image: Optional[str] = DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        reporting_slack_channel: Optional[str] = None,
        pull_request: PullRequest = None,
        should_save_report: bool = True,
        fail_fast: bool = False,
        fast_tests_only: bool = False,
        code_tests_only: bool = False,
        use_local_cdk: bool = False,
        use_host_gradle_dist_tar: bool = False,
        enable_report_auto_open: bool = True,
        docker_hub_username: Optional[str] = None,
        docker_hub_password: Optional[str] = None,
        s3_build_cache_access_key_id: Optional[str] = None,
        s3_build_cache_secret_key: Optional[str] = None,
        concurrent_cat: Optional[bool] = False,
    ):
        """Initialize a connector context.

        Args:
            connector (Connector): The connector under test.
            is_local (bool): Whether the context is for a local run or a CI run.
            git_branch (str): The current git branch name.
            git_revision (str): The current git revision, commit hash.
            report_output_prefix (str): The S3 key to upload the test report to.
            use_remote_secrets (bool, optional): Whether to download secrets for GSM or use the local secrets. Defaults to True.
            connector_acceptance_test_image (Optional[str], optional): The image to use to run connector acceptance tests. Defaults to DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE.
            gha_workflow_run_url (Optional[str], optional): URL to the github action workflow run. Only valid for CI run. Defaults to None.
            dagger_logs_url (Optional[str], optional): URL to the dagger logs. Only valid for CI run. Defaults to None.
            pipeline_start_timestamp (Optional[int], optional): Timestamp at which the pipeline started. Defaults to None.
            ci_context (Optional[str], optional): Pull requests, workflow dispatch or nightly build. Defaults to None.
            slack_webhook (Optional[str], optional): The slack webhook to send messages to. Defaults to None.
            reporting_slack_channel (Optional[str], optional): The slack channel to send messages to. Defaults to None.
            pull_request (PullRequest, optional): The pull request object if the pipeline was triggered by a pull request. Defaults to None.
            fail_fast (bool, optional): Whether to fail fast. Defaults to False.
            fast_tests_only (bool, optional): Whether to run only fast tests. Defaults to False.
            code_tests_only (bool, optional): Whether to ignore non-code tests like QA and metadata checks. Defaults to False.
            use_host_gradle_dist_tar (bool, optional): Used when developing java connectors with gradle. Defaults to False.
            enable_report_auto_open (bool, optional): Open HTML report in browser window. Defaults to True.
            docker_hub_username (Optional[str], optional): Docker Hub username to use to read registries. Defaults to None.
            docker_hub_password (Optional[str], optional): Docker Hub password to use to read registries. Defaults to None.
            s3_build_cache_access_key_id (Optional[str], optional): Gradle S3 Build Cache credentials. Defaults to None.
            s3_build_cache_secret_key (Optional[str], optional): Gradle S3 Build Cache credentials. Defaults to None.
            concurrent_cat (bool, optional): Whether to run the CAT tests in parallel. Defaults to False.
        """

        self.pipeline_name = pipeline_name
        self.connector = connector
        self.use_remote_secrets = use_remote_secrets
        self.connector_acceptance_test_image = connector_acceptance_test_image
        self.report_output_prefix = report_output_prefix
        self._secrets_dir = None
        self._updated_secrets_dir = None
        self.cdk_version = None
        self.should_save_report = should_save_report
        self.fail_fast = fail_fast
        self.fast_tests_only = fast_tests_only
        self.code_tests_only = code_tests_only
        self.use_local_cdk = use_local_cdk
        self.use_host_gradle_dist_tar = use_host_gradle_dist_tar
        self.enable_report_auto_open = enable_report_auto_open
        self.docker_hub_username = docker_hub_username
        self.docker_hub_password = docker_hub_password
        self.s3_build_cache_access_key_id = s3_build_cache_access_key_id
        self.s3_build_cache_secret_key = s3_build_cache_secret_key
        self.concurrent_cat = concurrent_cat

        super().__init__(
            pipeline_name=pipeline_name,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            dagger_logs_url=dagger_logs_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            slack_webhook=slack_webhook,
            reporting_slack_channel=reporting_slack_channel,
            pull_request=pull_request,
            ci_report_bucket=ci_report_bucket,
            ci_gcs_credentials=ci_gcs_credentials,
            ci_git_user=ci_git_user,
            ci_github_access_token=ci_github_access_token,
            enable_report_auto_open=enable_report_auto_open,
        )

    @property
    def s3_build_cache_access_key_id_secret(self) -> Optional[Secret]:
        if self.s3_build_cache_access_key_id:
            return self.dagger_client.set_secret("s3_build_cache_access_key_id", self.s3_build_cache_access_key_id)
        return None

    @property
    def s3_build_cache_secret_key_secret(self) -> Optional[Secret]:
        if self.s3_build_cache_access_key_id and self.s3_build_cache_secret_key:
            return self.dagger_client.set_secret("s3_build_cache_secret_key", self.s3_build_cache_secret_key)
        return None

    @property
    def modified_files(self):
        return self.connector.modified_files

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
    def docker_repository(self) -> str:
        return self.metadata["dockerRepository"]

    @property
    def docker_image_tag(self) -> str:
        return self.metadata["dockerImageTag"]

    @property
    def docker_image(self) -> str:
        return f"{self.docker_repository}:{self.docker_image_tag}"

    @property
    def docker_hub_username_secret(self) -> Optional[Secret]:
        if self.docker_hub_username is None:
            return None
        return self.dagger_client.set_secret("docker_hub_username", self.docker_hub_username)

    @property
    def docker_hub_password_secret(self) -> Optional[Secret]:
        if self.docker_hub_password is None:
            return None
        return self.dagger_client.set_secret("docker_hub_password", self.docker_hub_password)

    async def get_connector_dir(self, exclude=None, include=None) -> Directory:
        """Get the connector under test source code directory.

        Args:
            exclude ([List[str], optional): List of files or directories to exclude from the directory. Defaults to None.
            include ([List[str], optional): List of files or directories to include in the directory. Defaults to None.

        Returns:
            Directory: The connector under test source code directory.
        """
        vanilla_connector_dir = self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)
        return await vanilla_connector_dir.with_timestamps(1)

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

        if self.should_save_report:
            await self.report.save()

        await asyncify(update_commit_status_check)(**self.github_commit_status)

        if self.should_send_slack_message:
            await asyncify(send_message_to_webhook)(self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook)

        # Supress the exception if any
        return True

    def create_slack_message(self) -> str:
        raise NotImplementedError
