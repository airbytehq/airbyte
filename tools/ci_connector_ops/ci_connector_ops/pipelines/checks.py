#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups steps made to run checks (static code analysis) for a specific connector given a test context."""

from typing import List

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Step, StepResult


class QaChecks(Step):
    title = "QA checks"

    async def _run(self) -> List[StepResult]:
        """Runs our QA checks on a connector.
        The QA checks are defined in this module:
        https://github.com/airbytehq/airbyte/blob/master/tools/ci_connector_ops/ci_connector_ops/qa_checks.py

        Args:
            context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
        Returns:
            List[StepResult]: Failure or success of the QA checks with stdout and stdout in a list.
        """
        ci_connector_ops = await environments.with_ci_connector_ops(self.context)
        ci_connector_ops = self.get_dagger_pipeline(ci_connector_ops)
        filtered_repo = self.context.get_repo_dir(
            include=[
                str(self.context.connector.code_directory),
                str(self.context.connector.documentation_file_path),
                str(self.context.connector.icon_path),
                "airbyte-config/init/src/main/resources/seed/source_definitions.yaml",
                "airbyte-config/init/src/main/resources/seed/destination_definitions.yaml",
            ],
        )
        qa_checks = (
            ci_connector_ops.with_mounted_directory("/airbyte", filtered_repo)
            .with_workdir("/airbyte")
            .with_exec(["run-qa-checks", f"connectors/{self.context.connector.technical_name}"])
        )
        return [await self.get_step_result(qa_checks)]


class CodeFormatChecks(Step):
    title = "Code format checks"

    RUN_BLACK_CMD = ["python", "-m", "black", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check", "."]
    RUN_ISORT_CMD = ["python", "-m", "isort", f"--settings-file=/{environments.PYPROJECT_TOML_FILE_PATH}", "--check-only", "--diff", "."]
    RUN_FLAKE_CMD = ["python", "-m", "pflake8", f"--config=/{environments.PYPROJECT_TOML_FILE_PATH}", "."]

    async def _run(self) -> List[StepResult]:
        """Run a code format check on the container source code.
        We call black, isort and flake commands:
        - Black formats the code: fails if the code is not formatted.
        - Isort checks the import orders: fails if the import are not properly ordered.
        - Flake enforces style-guides: fails if the style-guide is not followed.
        Args:
            context (ConnectorTestContext): The current test context, providing a connector object, a dagger client and a repository directory.
            step (Step): The step in which the code format checks are run. Defaults to Step.CODE_FORMAT_CHECKS
        Returns:
            List[StepResult]: Failure or success of the code format checks with stdout and stdout in a list.
        """

        connector_under_test = environments.with_airbyte_connector(self.context)
        connector_under_test = self.get_dagger_pipeline(connector_under_test)
        formatter = (
            connector_under_test.with_exec(["echo", "Running black"])
            .with_exec(self.RUN_BLACK_CMD)
            .with_exec(["echo", "Running Isort"])
            .with_exec(self.RUN_ISORT_CMD)
            .with_exec(["echo", "Running Flake"])
            .with_exec(self.RUN_FLAKE_CMD)
        )
        return [await self.get_step_result(formatter)]
