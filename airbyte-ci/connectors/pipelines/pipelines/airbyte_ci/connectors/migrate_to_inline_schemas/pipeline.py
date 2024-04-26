#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

import dagger
from connector_ops.utils import ConnectorLanguage  # type: ignore
from packaging.version import Version
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.bump_version.pipeline import AddChangelogEntry, BumpDockerImageTagInMetadata
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun, run_steps
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore  # type: ignore

POETRY_LOCK_FILE = "poetry.lock"
POETRY_TOML_FILE = "pyproject.toml"


class CheckIsInlineCandidate(Step):
    """Check if the connector is a candidate to get inline schemas.
    Candidate conditions:
    - The connector is a Python connector.
    - The connector is a source connector.
    - The connector has a manifest file.
    - The connector has schemas directory.
    """

    context: ConnectorContext

    title = "Check if the connector is a candidate for inline schema migration."  # type: ignore

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:  # type: ignore
        connector_dir_entries = await (await self.context.get_connector_dir()).entries()
        if self.context.connector.language not in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a Python connector.",
            )
        if self.context.connector.connector_type != "source":
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a source connector.",
            )

        # TODO

        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class InlineSchemas(Step):
    context: ConnectorContext

    title = "Migrate connector to inline schemas."  # type: ignore

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:  # type: ignore
        self.logger.info("hey!")

        return StepResult(step=self, status=StepStatus.SUCCESS)


async def run_connector_migrate_to_inline_schemas_pipeline(context: ConnectorContext, semaphore: "Semaphore") -> Report:
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    steps_to_run: STEP_TREE = []

    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.INLINE_CANDIDATE, step=CheckIsInlineCandidate(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.INLINE_MIGRATION,
                step=InlineSchemas(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.INLINE_CANDIDATE],
            )
        ]
    )

    async with semaphore:
        async with context:
            try:
                result_dict = await run_steps(
                    runnables=steps_to_run,
                    options=context.run_step_options,
                )
            except Exception as e:
                raise e
            results = list(result_dict.values())
            report = ConnectorReport(context, steps_results=results, name="TEST RESULTS")
            context.report = report

    return report  # type: ignore
