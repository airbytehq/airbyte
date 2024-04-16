# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


from abc import ABC, abstractmethod
from functools import cached_property
from typing import ClassVar, Optional

import anyio
import requests  # type: ignore
import semver
import yaml  # type: ignore
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.consts import CIContext
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.helpers.utils import METADATA_FILE_NAME
from pipelines.models.steps import Step, StepResult, StepStatus


class VersionCheck(Step, ABC):
    """A step to validate the connector version was bumped if files were modified"""

    context: ConnectorContext
    GITHUB_URL_PREFIX_FOR_CONNECTORS = "https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-integrations/connectors"
    failure_message: ClassVar

    @property
    def should_run(self) -> bool:
        return True

    @property
    def github_master_metadata_url(self) -> str:
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
        return StepResult(step=self, status=StepStatus.SUCCESS)

    @property
    def failure_result(self) -> StepResult:
        return StepResult(step=self, status=StepStatus.FAILURE, stderr=self.failure_message)

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
    ]

    @property
    def failure_message(self) -> str:
        return f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented. The files you modified should lead to a version bump. Master version is {self.master_connector_version}, current version is {self.current_connector_version}"

    @property
    def should_run(self) -> bool:
        for filename in self.context.modified_files:
            relative_path = str(filename).replace(str(self.context.connector.code_directory) + "/", "")
            if not any([relative_path.startswith(to_bypass) for to_bypass in self.BYPASS_CHECK_FOR]):
                return True
        return False

    def validate(self) -> StepResult:
        if not self.current_connector_version > self.master_connector_version:
            return self.failure_result
        return self.success_result


async def run_check_version_increment_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """
    Compute the steps to run for a connector test pipeline.
    """
    all_steps_to_run: STEP_TREE = [
        [
            StepToRun(id=CONNECTOR_TEST_STEP_ID.VERSION_INC_CHECK, step=VersionIncrementCheck(context)),
        ]
    ]

    async with semaphore:
        async with context:
            result_dict = await run_steps(
                runnables=all_steps_to_run,
                options=context.run_step_options,
            )

            results = list(result_dict.values())
            report = ConnectorReport(context, steps_results=results, name="Version Increment Check Results")
            context.report = report

        return report
