#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch formatting steps according to the connector language."""

from __future__ import annotations

import sys
from typing import List, Optional

import anyio
import dagger
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import ConnectorReport, Step, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.format import java_connectors, python_connectors
from ci_connector_ops.pipelines.git import GitPushChanges
from ci_connector_ops.pipelines.pipelines.connectors import run_report_complete_pipeline
from ci_connector_ops.utils import ConnectorLanguage


class NoFormatStepForLanguageError(Exception):
    pass


FORMATTING_STEP_TO_CONNECTOR_LANGUAGE_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.FormatConnectorCode,
    ConnectorLanguage.LOW_CODE: python_connectors.FormatConnectorCode,
    ConnectorLanguage.JAVA: java_connectors.FormatConnectorCode,
}


class ExportChanges(Step):

    title = "Export changes to local repository"

    async def _run(self, changed_directory: dagger.Directory, changed_directory_path_in_repo: str) -> StepResult:
        await changed_directory.export(changed_directory_path_in_repo)
        return StepResult(self, StepStatus.SUCCESS, stdout=f"Changes exported to {changed_directory_path_in_repo}")


async def run_connector_format_pipeline(context: ConnectorContext) -> ConnectorReport:
    """Run a format pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding formats results.
    """
    steps_results = []
    async with context:
        FormatConnectorCode = FORMATTING_STEP_TO_CONNECTOR_LANGUAGE_MAPPING.get(context.connector.language)
        if not FormatConnectorCode:
            raise NoFormatStepForLanguageError(
                f"No formatting step found for connector {context.connector.technical_name} with language {context.connector.language}"
            )
        format_connector_code_result = await FormatConnectorCode(context).run()
        steps_results.append(format_connector_code_result)

        if context.is_local:
            export_changes_results = await ExportChanges(context).run(
                format_connector_code_result.output_artifact, str(context.connector.code_directory)
            )
            steps_results.append(export_changes_results)
        else:
            git_push_changes_results = await GitPushChanges(context).run(
                format_connector_code_result.output_artifact,
                str(context.connector.code_directory),
                f"Auto format {context.connector.technical_name} code",
                skip_ci=True,
            )
            steps_results.append(git_push_changes_results)
        context.report = ConnectorReport(context, steps_results, name="FORMAT RESULTS")
    return context.report


async def run_connectors_format_pipelines(
    contexts: List[ConnectorContext],
    ci_git_user: str,
    ci_github_access_token: str,
    git_branch: str,
    is_local: bool,
    execute_timeout: Optional[int],
) -> List[ConnectorContext]:

    async with dagger.Connection(dagger.Config(log_output=sys.stderr, execute_timeout=execute_timeout)) as dagger_client:
        requires_dind = any(context.connector.language == ConnectorLanguage.JAVA for context in contexts)
        dockerd_service = environments.with_global_dockerd_service(dagger_client)
        async with anyio.create_task_group() as tg_main:
            if requires_dind:
                tg_main.start_soon(dockerd_service.sync)
                await anyio.sleep(10)  # Wait for the docker service to be ready
            for context in contexts:
                context.dagger_client = dagger_client.pipeline(f"Format - {context.connector.technical_name}")
                context.dockerd_service = dockerd_service
                await run_connector_format_pipeline(context)
            # When the connectors pipelines are done, we can stop the dockerd service
            tg_main.cancel_scope.cancel()

        await run_report_complete_pipeline(dagger_client, contexts)

    return contexts
