#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module declaring context related classes."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING

import yaml  # type: ignore
from asyncer import asyncify
from dagger import Directory, Platform
from github import PullRequest
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.consts import BUILD_PLATFORMS
from pipelines.dagger.actions import secrets
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles
from pipelines.helpers.execution.run_steps import RunStepOptions
from pipelines.helpers.github import update_commit_status_check
from pipelines.helpers.slack import send_message_to_webhook
from pipelines.helpers.utils import METADATA_FILE_NAME
from pipelines.models.contexts.pipeline_context import PipelineContext
from pipelines.models.secrets import LocalDirectorySecretStore, Secret, SecretNotFoundError, SecretStore
from pydash import find  # type: ignore

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path as NativePath
    from typing import Dict, FrozenSet, List, Optional, Sequence
# These test suite names are declared in metadata.yaml files
TEST_SUITE_NAME_TO_STEP_ID = {
    "unitTests": CONNECTOR_TEST_STEP_ID.UNIT,
    "integrationTests": CONNECTOR_TEST_STEP_ID.INTEGRATION,
    "acceptanceTests": CONNECTOR_TEST_STEP_ID.ACCEPTANCE,
}


class ConnectorContext(PipelineContext):
    """The connector context is used to store configuration for a specific connector pipeline run."""

    DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE = "airbyte/connector-acceptance-test:dev"

    def __init__(
        self,
        pipeline_name: str,
        connector: ConnectorWithModifiedFiles,
        is_local: bool,
        git_branch: str,
        git_revision: str,
        diffed_branch: str,
        git_repo_url: str,
        report_output_prefix: str,
        ci_report_bucket: Optional[str] = None,
        ci_gcp_credentials: Optional[Secret] = None,
        ci_git_user: Optional[str] = None,
        ci_github_access_token: Optional[Secret] = None,
        connector_acceptance_test_image: str = DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE,
        gha_workflow_run_url: Optional[str] = None,
        dagger_logs_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        reporting_slack_channel: Optional[str] = None,
        pull_request: Optional[PullRequest.PullRequest] = None,
        should_save_report: bool = True,
        code_tests_only: bool = False,
        use_local_cdk: bool = False,
        use_host_gradle_dist_tar: bool = False,
        enable_report_auto_open: bool = True,
        docker_hub_username: Optional[Secret] = None,
        docker_hub_password: Optional[Secret] = None,
        s3_build_cache_access_key_id: Optional[Secret] = None,
        s3_build_cache_secret_key: Optional[Secret] = None,
        concurrent_cat: Optional[bool] = False,
        run_step_options: RunStepOptions = RunStepOptions(),
        targeted_platforms: Sequence[Platform] = BUILD_PLATFORMS,
        secret_stores: Dict[str, SecretStore] | None = None,
    ) -> None:
        """Initialize a connector context.

        Args:
            connector (Connector): The connector under test.
            is_local (bool): Whether the context is for a local run or a CI run.
            git_branch (str): The current git branch name.
            git_revision (str): The current git revision, commit hash.
            diffed_branch: str: The branch to compare the current branch against.
            git_repo_url: str: The URL of the git repository.
            report_output_prefix (str): The S3 key to upload the test report to.
            connector_acceptance_test_image (Optional[str], optional): The image to use to run connector acceptance tests. Defaults to DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE.
            gha_workflow_run_url (Optional[str], optional): URL to the github action workflow run. Only valid for CI run. Defaults to None.
            dagger_logs_url (Optional[str], optional): URL to the dagger logs. Only valid for CI run. Defaults to None.
            pipeline_start_timestamp (Optional[int], optional): Timestamp at which the pipeline started. Defaults to None.
            ci_context (Optional[str], optional): Pull requests, workflow dispatch or nightly build. Defaults to None.
            slack_webhook (Optional[str], optional): The slack webhook to send messages to. Defaults to None.
            reporting_slack_channel (Optional[str], optional): The slack channel to send messages to. Defaults to None.
            pull_request (PullRequest, optional): The pull request object if the pipeline was triggered by a pull request. Defaults to None.
            code_tests_only (bool, optional): Whether to ignore non-code tests like QA and metadata checks. Defaults to False.
            use_host_gradle_dist_tar (bool, optional): Used when developing java connectors with gradle. Defaults to False.
            enable_report_auto_open (bool, optional): Open HTML report in browser window. Defaults to True.
            docker_hub_username (Optional[Secret], optional): Docker Hub username to use to read registries. Defaults to None.
            docker_hub_password (Optional[Secret], optional): Docker Hub password to use to read registries. Defaults to None.
            s3_build_cache_access_key_id (Optional[Secret], optional): Gradle S3 Build Cache credentials. Defaults to None.
            s3_build_cache_secret_key (Optional[Secret], optional): Gradle S3 Build Cache credentials. Defaults to None.
            concurrent_cat (bool, optional): Whether to run the CAT tests in parallel. Defaults to False.
            targeted_platforms (Optional[Iterable[Platform]], optional): The platforms to build the connector image for. Defaults to BUILD_PLATFORMS.
        """

        self.pipeline_name = pipeline_name
        self.connector = connector
        self.connector_acceptance_test_image = connector_acceptance_test_image
        self._secrets_dir: Optional[Directory] = None
        self._updated_secrets_dir: Optional[Directory] = None
        self.cdk_version: Optional[str] = None
        self.should_save_report = should_save_report
        self.code_tests_only = code_tests_only
        self.use_local_cdk = use_local_cdk
        self.use_host_gradle_dist_tar = use_host_gradle_dist_tar
        self.enable_report_auto_open = enable_report_auto_open
        self.docker_hub_username = docker_hub_username
        self.docker_hub_password = docker_hub_password
        self.s3_build_cache_access_key_id = s3_build_cache_access_key_id
        self.s3_build_cache_secret_key = s3_build_cache_secret_key
        self.concurrent_cat = concurrent_cat
        self.targeted_platforms = targeted_platforms
        super().__init__(
            pipeline_name=pipeline_name,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            diffed_branch=diffed_branch,
            git_repo_url=git_repo_url,
            report_output_prefix=report_output_prefix,
            gha_workflow_run_url=gha_workflow_run_url,
            dagger_logs_url=dagger_logs_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
            slack_webhook=slack_webhook,
            reporting_slack_channel=reporting_slack_channel,
            pull_request=pull_request,
            ci_report_bucket=ci_report_bucket,
            ci_gcp_credentials=ci_gcp_credentials,
            ci_git_user=ci_git_user,
            ci_github_access_token=ci_github_access_token,
            run_step_options=self._skip_metadata_disabled_test_suites(run_step_options),
            enable_report_auto_open=enable_report_auto_open,
            secret_stores=secret_stores,
        )
        self.step_id_to_secrets_mapping = self._get_step_id_to_secret_mapping()

    @property
    def modified_files(self) -> FrozenSet[NativePath]:
        return self.connector.modified_files

    @property
    def secrets_dir(self) -> Optional[Directory]:
        return self._secrets_dir

    @secrets_dir.setter
    def secrets_dir(self, secrets_dir: Directory) -> None:
        self._secrets_dir = secrets_dir

    @property
    def updated_secrets_dir(self) -> Optional[Directory]:
        return self._updated_secrets_dir

    @updated_secrets_dir.setter
    def updated_secrets_dir(self, updated_secrets_dir: Directory) -> None:
        self._updated_secrets_dir = updated_secrets_dir

    @property
    def connector_acceptance_test_source_dir(self) -> Directory:
        return self.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")

    @property
    def live_tests_dir(self) -> Directory:
        return self.get_repo_dir("airbyte-ci/connectors/live-tests")

    @property
    def should_save_updated_secrets(self) -> bool:
        return self.ci_gcp_credentials is not None and self.updated_secrets_dir is not None

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
    def local_secret_store_name(self) -> str:
        return f"{self.connector.technical_name}-local"

    @property
    def local_secret_store(self) -> Optional[LocalDirectorySecretStore]:
        connector_secrets_path = self.connector.code_directory / "secrets"
        if connector_secrets_path.is_dir():
            return LocalDirectorySecretStore(connector_secrets_path)
        return None

    async def get_connector_dir(self, exclude: Optional[List[str]] = None, include: Optional[List[str]] = None) -> Directory:
        """Get the connector under test source code directory.

        Args:
            exclude ([List[str], optional): List of files or directories to exclude from the directory. Defaults to None.
            include ([List[str], optional): List of files or directories to include in the directory. Defaults to None.

        Returns:
            Directory: The connector under test source code directory.
        """
        vanilla_connector_dir = self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)
        return await vanilla_connector_dir.with_timestamps(1)

    @staticmethod
    def _handle_missing_secret_store(
        secret_info: Dict[str, str | Dict[str, str]], raise_on_missing: bool, logger: Optional[Logger] = None
    ) -> None:
        assert isinstance(secret_info["secretStore"], dict), "The secretStore field must be a dict"
        message = f"Secret {secret_info['name']} can't be retrieved as {secret_info['secretStore']['alias']} is not available"
        if raise_on_missing:
            raise SecretNotFoundError(message)
        if logger is not None:
            logger.warn(message)

    @staticmethod
    def _process_secret(
        secret_info: Dict[str, str | Dict[str, str]],
        secret_stores: Dict[str, SecretStore],
        raise_on_missing: bool,
        logger: Optional[Logger] = None,
    ) -> Optional[Secret]:
        assert isinstance(secret_info["secretStore"], dict), "The secretStore field must be a dict"
        secret_store_alias = secret_info["secretStore"]["alias"]
        if secret_store_alias not in secret_stores:
            ConnectorContext._handle_missing_secret_store(secret_info, raise_on_missing, logger)
            return None
        else:
            # All these asserts and casting are there to make MyPy happy
            # The dict structure being nested MyPy can't figure if the values are str or dict
            assert isinstance(secret_info["name"], str), "The secret name field must be a string"
            if file_name := secret_info.get("fileName"):
                assert isinstance(secret_info["fileName"], str), "The secret fileName must be a string"
                file_name = str(secret_info["fileName"])
            else:
                file_name = None
            return Secret(secret_info["name"], secret_stores[secret_store_alias], file_name=file_name)

    @staticmethod
    def get_secrets_from_connector_test_suites_option(
        connector_test_suites_options: List[Dict[str, str | Dict[str, List[Dict[str, str | Dict[str, str]]]]]],
        suite_name: str,
        secret_stores: Dict[str, SecretStore],
        raise_on_missing_secret_store: bool = True,
        logger: Logger | None = None,
    ) -> List[Secret]:
        """Get secrets declared in metadata connectorTestSuitesOptions for a test suite name.
        It will use the secret store alias declared in connectorTestSuitesOptions.
        If the secret store is not available a warning or and error could be raised according to the raise_on_missing_secret_store parameter value.
        We usually want to raise an error when running in CI context and log a warning when running locally, as locally we can fallback on local secrets.

        Args:
            connector_test_suites_options (List[Dict[str, str  |  Dict]]): The connector under test test suite options
            suite_name (str): The test suite name
            secret_stores (Dict[str, SecretStore]): The available secrets stores
            raise_on_missing_secret_store (bool, optional): Raise an error if the secret store declared in the connectorTestSuitesOptions is not available. Defaults to True.
            logger (Logger | None, optional): Logger to log a warning if the secret store declared in the connectorTestSuitesOptions is not available. Defaults to None.

        Raises:
            SecretNotFoundError: Raised  if the secret store declared in the connectorTestSuitesOptions is not available and raise_on_missing_secret_store is truthy.

        Returns:
            List[Secret]: List of secrets declared in the connectorTestSuitesOptions for a test suite name.
        """
        secrets: List[Secret] = []
        enabled_test_suite = find(connector_test_suites_options, lambda x: x["suite"] == suite_name)

        if enabled_test_suite and "testSecrets" in enabled_test_suite:
            for secret_info in enabled_test_suite["testSecrets"]:
                if secret := ConnectorContext._process_secret(secret_info, secret_stores, raise_on_missing_secret_store, logger):
                    secrets.append(secret)

        return secrets

    def get_connector_secrets_for_test_suite(
        self, test_suite_name: str, connector_test_suites_options: List, local_secrets: List[Secret]
    ) -> List[Secret]:
        """Get secrets to use for a test suite.
        Always merge secrets declared in metadata's connectorTestSuiteOptions with secrets declared locally.

        Args:
            test_suite_name (str): Name of the test suite to get secrets for
            context (ConnectorContext): The current connector context
            connector_test_suites_options (Dict): The current connector test suite options (from metadata)
            local_secrets (List[Secret]): The local connector secrets.

        Returns:
            List[Secret]: Secrets to use to run the passed test suite name.
        """
        return (
            self.get_secrets_from_connector_test_suites_option(
                connector_test_suites_options,
                test_suite_name,
                self.secret_stores,
                raise_on_missing_secret_store=self.is_ci,
                logger=self.logger,
            )
            + local_secrets
        )

    def _get_step_id_to_secret_mapping(self) -> Dict[CONNECTOR_TEST_STEP_ID, List[Secret]]:
        step_id_to_secrets: Dict[CONNECTOR_TEST_STEP_ID, List[Secret]] = {
            CONNECTOR_TEST_STEP_ID.UNIT: [],
            CONNECTOR_TEST_STEP_ID.INTEGRATION: [],
            CONNECTOR_TEST_STEP_ID.ACCEPTANCE: [],
        }
        local_secrets = self.local_secret_store.get_all_secrets() if self.local_secret_store else []
        connector_test_suites_options = self.metadata.get("connectorTestSuitesOptions", [])

        keep_steps = set(self.run_step_options.keep_steps or [])
        skip_steps = set(self.run_step_options.skip_steps or [])

        for test_suite_name, step_id in TEST_SUITE_NAME_TO_STEP_ID.items():
            if step_id in keep_steps or (not keep_steps and step_id not in skip_steps):
                step_id_to_secrets[step_id] = self.get_connector_secrets_for_test_suite(
                    test_suite_name, connector_test_suites_options, local_secrets
                )
        return step_id_to_secrets

    def get_secrets_for_step_id(self, step_id: CONNECTOR_TEST_STEP_ID) -> List[Secret]:
        return self.step_id_to_secrets_mapping.get(step_id, [])

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
            # Using a type ignore here because the should_send_slack_message property is checking for non nullity of the slack_webhook and reporting_slack_channel
            await asyncify(send_message_to_webhook)(self.create_slack_message(), self.reporting_slack_channel, self.slack_webhook)  # type: ignore

        # Supress the exception if any
        return True

    def create_slack_message(self) -> str:
        raise NotImplementedError

    def _get_step_id_to_skip_according_to_metadata(self) -> List[CONNECTOR_TEST_STEP_ID]:
        """The connector metadata have a connectorTestSuitesOptions field.
        It allows connector developers to declare the test suites that are enabled for a connector.
        This function retrieved enabled test suites according to this field value and returns the test suites steps that are skipped (because they're not declared in this field.)
        The skippable test suites steps are declared in TEST_SUITE_NAME_TO_STEP_ID.

        Returns:
            List[CONNECTOR_TEST_STEP_ID]: List of step ids that should be skipped according to connector metadata.
        """
        enabled_test_suites = [option["suite"] for option in self.metadata.get("connectorTestSuitesOptions", [])]
        return [step_id for test_suite_name, step_id in TEST_SUITE_NAME_TO_STEP_ID.items() if test_suite_name not in enabled_test_suites]

    def _skip_metadata_disabled_test_suites(self, run_step_options: RunStepOptions) -> RunStepOptions:
        """Updated the original run_step_options to skip the disabled test suites according to connector metadata.

        Args:
            run_step_options (RunStepOptions): Original run step options.

        Returns:
            RunStepOptions: Updated run step options.
        """
        run_step_options = deepcopy(run_step_options)
        # If any `skip_steps` are present, we will run everything except the skipped steps, instead of just `keep_steps`.
        if not run_step_options.keep_steps:
            run_step_options.skip_steps += self._get_step_id_to_skip_according_to_metadata()
        return run_step_options
