#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import TYPE_CHECKING, Any, List, Set
import shutil
import tempfile

from pathlib import Path
from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.connectors.format import format_prettier
from pipelines.helpers.connectors.yaml import read_yaml, write_yaml
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus


if TYPE_CHECKING:
    from anyio import Semaphore  # type: ignore


class RestoreOriginalState(Step):
    context: ConnectorContext

    title = "Restore original state"  # type: ignore

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)

    async def _run(self) -> StepResult:  # type: ignore
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )

    async def _cleanup(self) -> StepResult:  # type: ignore
        return StepResult(
            step=self,
            status=StepStatus.SUCCESS,
        )


class CreatePullRequest(Step):
    context: ConnectorContext

    title = "Migrate connector to inline schemas."  # type: ignore

    def __init__(self, context: ConnectorContext, all_modified_files: Set[Path]) -> None:
        super().__init__(context)
        self.connector_files = filter_to_changes_in_connector(context, all_modified_files)

    async def _run(self) -> StepResult:  # type: ignore
        if len(self.connector_files) == 0:
            return StepResult(step=self, status=StepStatus.SKIPPED, stderr="Files modified in this connector.")

        connector = self.context.connector
        connector_path = connector.code_directory
        manifest_path = connector.manifest_path
        python_path = connector.python_source_dir_path
        logger = self.logger

        for file in self.connector_files:
            logger.info(f"Modified file: {file}")

        return StepResult(step=self, status=StepStatus.SUCCESS)


def filter_to_changes_in_connector(context: ConnectorContext, all_modified_files: Set[Path]) -> Set[Path]:
    directory = context.connector.code_directory
    # get a list of files that are a child of this path
    connector_files = set([file for file in all_modified_files if directory in file.parents])
    # get doc too
    doc_path = context.connector.documentation_file_path

    if doc_path in all_modified_files:
        connector_files.add(doc_path)

    return connector_files


async def run_connector_pull_request(context: ConnectorContext, semaphore: "Semaphore", modified_files: Set[Path]) -> Report:
    restore_original_state = RestoreOriginalState(context)

    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    steps_to_run: STEP_TREE = []

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.PULL_REQUEST_CREATE,
                step=CreatePullRequest(context, modified_files),
                depends_on=[],
            )
        ]
    )

    return await run_connector_steps(context, semaphore, steps_to_run, restore_original_state=restore_original_state)
