#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests agnostic to a connector language."""

from abc import ABC, abstractmethod
from functools import cached_property
from typing import ClassVar, Optional

import asyncer
import requests
import semver
import yaml
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import CIContext, PytestStep, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.utils import METADATA_FILE_NAME
from ci_connector_ops.utils import Connector
from dagger import File


class VersionCheck(Step, ABC):
    """A step to validate the connector version was bumped if files were modified"""

    GITHUB_URL_PREFIX_FOR_CONNECTORS = "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors"
    failure_message: ClassVar
    should_run = True

    @property
    def github_master_metadata_url(self):
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
        return StepResult(self, status=StepStatus.SUCCESS)

    @property
    def failure_result(self) -> StepResult:
        return StepResult(self, status=StepStatus.FAILURE, stderr=self.failure_message)

    @abstractmethod
    def validate(self) -> StepResult:
        raise NotImplementedError()

    async def _run(self) -> StepResult:
        if not self.should_run:
            return StepResult(self, status=StepStatus.SKIPPED, stdout="No modified files required a version bump.")
        if self.context.ci_context in [CIContext.MASTER, CIContext.NIGHTLY_BUILDS]:
            return StepResult(self, status=StepStatus.SKIPPED, stdout="Version check are not running in master context.")
        try:
            return self.validate()
        except (requests.HTTPError, ValueError, TypeError) as e:
            return StepResult(self, status=StepStatus.FAILURE, stderr=str(e))


class VersionIncrementCheck(VersionCheck):
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
            relative_path = filename.replace(str(self.context.connector.code_directory) + "/", "")
            if not any([relative_path.startswith(to_bypass) for to_bypass in self.BYPASS_CHECK_FOR]):
                return True
        return False

    def validate(self) -> StepResult:
        if not self.current_connector_version > self.master_connector_version:
            return self.failure_result
        return self.success_result


class VersionFollowsSemverCheck(VersionCheck):
    title = "Connector version semver check"

    @property
    def failure_message(self) -> str:
        return f"The dockerImageTag in {METADATA_FILE_NAME} is not following semantic versioning or was decremented. Master version is {self.master_connector_version}, current version is {self.current_connector_version}"

    def validate(self) -> StepResult:
        try:
            if not self.current_connector_version >= self.master_connector_version:
                return self.failure_result
        except ValueError:
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
        include = [
            str(self.context.connector.code_directory),
            str(self.context.connector.documentation_file_path),
            str(self.context.connector.migration_guide_file_path),
            str(self.context.connector.icon_path),
        ]
        if (
            self.context.connector.technical_name.endswith("strict-encrypt")
            or self.context.connector.technical_name == "source-file-secure"
        ):
            original_connector = Connector(self.context.connector.technical_name.replace("-strict-encrypt", "").replace("-secure", ""))
            include += [
                str(original_connector.code_directory),
                str(original_connector.documentation_file_path),
                str(original_connector.icon_path),
            ]

        filtered_repo = self.context.get_repo_dir(
            include=include,
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
        logs = soon_cat_container_stdout.value
        if self.context.is_local:
            await self.write_log_file(logs)
        return self.pytest_logs_to_step_result(logs)
