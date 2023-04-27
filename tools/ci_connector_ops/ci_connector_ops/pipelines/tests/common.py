#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests agnostic to a connector language."""

from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import ClassVar, Optional

import asyncer
import requests
import yaml
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import PytestStep, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import CIContext, PipelineContext
from ci_connector_ops.pipelines.utils import METADATA_FILE_NAME
from ci_connector_ops.utils import DESTINATION_DEFINITIONS_FILE_PATH, SOURCE_DEFINITIONS_FILE_PATH
from dagger import File
from packaging import version


class VersionCheck(Step, ABC):
    """A step to validate the connector version was bumped if files were modified"""

    GITHUB_URL_PREFIX_FOR_CONNECTORS = "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors"
    failure_message: ClassVar

    def __init__(self, context: PipelineContext, metadata_path: Path) -> None:
        super().__init__(context)
        self.current_metadata = yaml.safe_load(metadata_path.read_text())["data"]
        self.connector_technical_name = self.metadata["dockerRepository"].split("/")[-1]

    @property
    def github_master_metadata_url(self):
        return f"{self.GITHUB_URL_PREFIX_FOR_CONNECTORS}/{self.connector_technical_name}/{METADATA_FILE_NAME}"

    @cached_property
    def master_metadata(self) -> dict:
        response = requests.get(self.github_master_metadata_url)
        response.raise_for_status()
        return yaml.safe_load(response.text)

    @property
    def master_connector_version(self) -> version.Version:
        metadata = self.master_metadata
        return version.parse(str(metadata["data"]["dockerImageTag"]))

    @property
    def current_connector_version(self) -> version.Version:
        return version.parse(str(self.current_metadata["dockerImageTag"]))

    @property
    def success_result(self) -> StepResult:
        return StepResult(self, status=StepStatus.SUCCESS)

    @property
    def failure_result(self) -> StepResult:
        return StepResult(self, status=StepStatus.FAILURE, stderr=self.failure_message)

    @abstractmethod
    def validate(self) -> StepResult:
        raise NotImplementedError()

    async def _run(self) -> StepResult:
        if not self.context.modified_files:
            return StepResult(self, status=StepStatus.SKIPPED, stdout="No modified files.")
        if self.context.ci_context is CIContext.MASTER:
            return StepResult(self, status=StepStatus.SKIPPED, stdout="Version check are not running in master context.")
        try:
            return self.validate()
        except (requests.HTTPError, version.InvalidVersion, TypeError) as e:
            return StepResult(self, status=StepStatus.FAILURE, stderr=str(e))


class VersionIncrementCheck(VersionCheck):

    title = "Connector version increment check."
    failure_message = f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented."

    def validate(self) -> StepResult:
        if not self.current_connector_version > self.master_connector_version:
            return self.failure_result
        return self.success_result


class VersionFollowsSemverCheck(VersionCheck):

    title = "Connector version semver check."
    failure_message = f"The dockerImageTag in {METADATA_FILE_NAME} is not following semantic versioning."

    def validate(self) -> StepResult:
        if not len(str(self.current_connector_version).split(".")) == 3:
            return self.failure_result
        return self.success_result


class QaChecks(Step):
    """A step to run QA checks for a connector."""

    title = "QA checks"

    async def _run(self) -> StepResult:
        """Run QA checks on a connector.

        The QA checks are defined in this module:
        https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/qa_checks.py

        Args:
            context (ConnectorContext): The current test context, providing a connector object, a dagger client and a repository directory.
        Returns:
            StepResult: Failure or success of the QA checks with stdout and stderr.
        """
        ci_connector_ops = await environments.with_ci_connector_ops(self.context)
        filtered_repo = self.context.get_repo_dir(
            include=[
                str(self.context.connector.code_directory),
                str(self.context.connector.documentation_file_path),
                str(self.context.connector.icon_path),
                SOURCE_DEFINITIONS_FILE_PATH,
                DESTINATION_DEFINITIONS_FILE_PATH,
            ],
        )
        qa_checks = (
            ci_connector_ops.with_mounted_directory("/airbyte", filtered_repo)
            .with_workdir("/airbyte")
            .with_exec(["run-qa-checks", f"connectors/{self.context.connector.technical_name}"])
        )
        return await self.get_step_result(qa_checks)


class AcceptanceTests(PytestStep):
    """A step to run acceptance tests for a connector if it has an acceptance test config file."""

    title = "Acceptance tests"

    async def _run(self, connector_under_test_image_tar: Optional[File]) -> StepResult:
        """Run the acceptance test suite on a connector dev image. Build the connector acceptance test image if the tag is :dev.

        Args:
            connector_under_test_image_tar (File): The file holding the tar archive of the connector image.

        Returns:
            StepResult: Failure or success of the acceptances tests with stdout and stderr.
        """
        if not self.context.connector.acceptance_test_config:
            return StepResult(self, StepStatus.SKIPPED)

        cat_container = await environments.with_connector_acceptance_test(self.context, connector_under_test_image_tar)
        secret_dir = cat_container.directory("/test_input/secrets")

        async with asyncer.create_task_group() as task_group:
            soon_secret_files = task_group.soonify(secret_dir.entries)()
            soon_cat_container_stdout = task_group.soonify(cat_container.stdout)()

        if secret_files := soon_secret_files.value:
            for file_path in secret_files:
                if file_path.startswith("updated_configurations"):
                    self.context.updated_secrets_dir = secret_dir
                    break

        return self.pytest_logs_to_step_result(soon_cat_container_stdout.value)
