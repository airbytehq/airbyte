#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups steps made to run tests agnostic to a connector language."""

from typing import Optional

import asyncer
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import PytestStep, Step, StepResult, StepStatus
from ci_connector_ops.utils import DESTINATION_DEFINITIONS_FILE_PATH, SOURCE_DEFINITIONS_FILE_PATH
from dagger import File


class QaChecks(Step):
    """A step to run QA checks for a connector."""

    title = "QA checks"

    async def _run(self) -> StepResult:
        """Run QA checks on a connector.

        The QA checks are defined in this module:
        https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/qa_checks.py

        Args:
            context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
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
