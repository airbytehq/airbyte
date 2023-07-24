#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups the functions to run full pipelines for connector testing."""

import sys
from pathlib import Path
from typing import Callable, List, Optional

import anyio
import dagger
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import NoOpStep, Report, StepResult, StepStatus
from ci_connector_ops.pipelines.contexts import ConnectorContext, ContextState
from ci_connector_ops.utils import ConnectorLanguage
from dagger import Config

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"

CONNECTOR_LANGUAGE_TO_FORCED_CONCURRENCY_MAPPING = {
    # We run the Java connectors tests sequentially because we currently have memory issues when Java integration tests are run in parallel.
    # See https://github.com/airbytehq/airbyte/issues/27168
    ConnectorLanguage.JAVA: anyio.Semaphore(1),
}


async def context_to_step_result(context: ConnectorContext) -> StepResult:
    if context.state == ContextState.SUCCESSFUL:
        return await NoOpStep(context, StepStatus.SUCCESS).run()

    if context.state == ContextState.FAILURE:
        return await NoOpStep(context, StepStatus.FAILURE).run()

    if context.state == ContextState.ERROR:
        return await NoOpStep(context, StepStatus.FAILURE).run()

    raise ValueError(f"Could not convert context state: {context.state} to step status")


# HACK: This is to avoid wrapping the whole pipeline in a dagger pipeline to avoid instability just prior to launch
# TODO (ben): Refactor run_connectors_pipelines to wrap the whole pipeline in a dagger pipeline once Steps are refactored
async def run_report_complete_pipeline(dagger_client: dagger.Client, contexts: List[ConnectorContext]) -> List[ConnectorContext]:
    """Create and Save a report representing the run of the encompassing pipeline.

    This is to denote when the pipeline is complete, useful for long running pipelines like nightlies.
    """

    if not contexts:
        return []

    # Repurpose the first context to be the pipeline upload context to preserve timestamps
    first_connector_context = contexts[0]

    pipeline_name = f"Report upload {first_connector_context.report_output_prefix}"
    first_connector_context.pipeline_name = pipeline_name

    # Transform contexts into a list of steps
    steps_results = [await context_to_step_result(context) for context in contexts]

    report = Report(
        name=pipeline_name,
        pipeline_context=first_connector_context,
        steps_results=steps_results,
        filename="complete",
    )

    return await report.save()


async def run_connectors_pipelines(
    contexts: List[ConnectorContext],
    connector_pipeline: Callable,
    pipeline_name: str,
    concurrency: int,
    dagger_logs_path: Optional[Path],
    execute_timeout: Optional[int],
    *args,
) -> List[ConnectorContext]:
    """Run a connector pipeline for all the connector contexts."""

    default_connectors_semaphore = anyio.Semaphore(concurrency)
    dagger_logs_output = sys.stderr if not dagger_logs_path else open(dagger_logs_path, "w")
    async with dagger.Connection(Config(log_output=dagger_logs_output, execute_timeout=execute_timeout)) as dagger_client:
        # HACK: This is to get a long running dockerd service to be shared across all the connectors pipelines
        # Using the "normal" service binding leads to restart of dockerd during pipeline run that can cause corrupted docker state
        # See https://github.com/airbytehq/airbyte/issues/27233
        dockerd_service = environments.with_global_dockerd_service(dagger_client)
        async with anyio.create_task_group() as tg_main:
            tg_main.start_soon(dockerd_service.sync)
            await anyio.sleep(10)  # Wait for the docker service to be ready
            async with anyio.create_task_group() as tg_connectors:
                for context in contexts:
                    context.dagger_client = dagger_client.pipeline(f"{pipeline_name} - {context.connector.technical_name}")
                    context.dockerd_service = dockerd_service
                    tg_connectors.start_soon(
                        connector_pipeline,
                        context,
                        CONNECTOR_LANGUAGE_TO_FORCED_CONCURRENCY_MAPPING.get(context.connector.language, default_connectors_semaphore),
                        *args,
                    )
            # When the connectors pipelines are done, we can stop the dockerd service
            tg_main.cancel_scope.cancel()
        await run_report_complete_pipeline(dagger_client, contexts)

    return contexts
