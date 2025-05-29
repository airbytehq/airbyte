#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


class CheckIsMigrationCandidate(Step):
    """Check if the connector is a candidate to get replace the AirbyteLogger.
    Candidate conditions:
    - The connector is a Python connector.
    """

    context: ConnectorContext

    title = "Check if the connector is a candidate for re."

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:
        connector = self.context.connector
        if connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a Python connector.",
            )

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class MigrateAirbyteLogger(Step):
    context: ConnectorContext

    title = "Migrate connector to replace AirbyteLogger with logging.Logger. It is recommended to run `airbyte-ci format fix python` after running this command."

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:
        connector = self.context.connector
        python_path = connector.code_directory
        file_path = Path(os.path.abspath(os.path.join(python_path)))

        self.replace_text_in_files(file_path, "from airbyte_cdk import AirbyteLogger", "import logging")
        self.replace_text_in_files(file_path, "from airbyte_cdk.logger import AirbyteLogger", "import logging")
        self.replace_text_in_files(file_path, "logger: AirbyteLogger", "logger: logging.Logger")
        self.replace_text_in_files(file_path, "AirbyteLogger()", 'logging.getLogger("airbyte")')

        return StepResult(step=self, status=StepStatus.SUCCESS)

    def replace_text_in_files(self, root_dir: Path, old_text: str, new_text: str) -> None:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, "r", encoding="utf-8") as file:
                        content = file.read()

                    new_content = content.replace(old_text, new_text)

                    if new_content != content:
                        with open(filepath, "w", encoding="utf-8") as file:
                            file.write(new_content)


async def run_connector_migrate_to_logging_logger_pipeline(context: ConnectorContext, semaphore: "Semaphore") -> Report:
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    steps_to_run: STEP_TREE = []

    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.AIRBYTE_LOGGER_CANDIDATE, step=CheckIsMigrationCandidate(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.AIRBYTE_LOGGER_MIGRATION,
                step=MigrateAirbyteLogger(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.AIRBYTE_LOGGER_CANDIDATE],
            )
        ]
    )

    return await run_connector_steps(context, semaphore, steps_to_run)
