#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups the functions to run full pipelines for connector testing."""

import sys
from typing import Callable, List, Optional, TYPE_CHECKING

import anyio
import dagger
from dagger import Config

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.bases import Report, StepResult
from ci_connector_ops.pipelines.contexts import ConnectorContext

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"


# HACK: This is to avoid wrapping the whole pipeline in a dagger pipeline to avoid instability just prior to launch
# TODO (ben): Refactor run_connectors_pipelines to wrap the whole pipeline in a dagger pipeline
async def run_report_upload_pipeline(dagger_client: dagger.Client, contexts: List[ConnectorContext]) -> List[ConnectorContext]:
    first_connector_context = contexts[0]
    pipeline_name = f"Report upload {first_connector_context.report_output_prefix}"
    first_connector_context.pipeline_name = pipeline_name

    # Transform contexts into a list of steps
    steps_results = [StepResult(step=None, status=context.state.to_step_status) for context in contexts]

    report = Report(
        name=pipeline_name,
        pipeline_context=first_connector_context,
        steps_results=steps_results,
    )

    file_path_key = f"{first_connector_context.report_output_prefix}/complete.json"
    return await report.save(file_path_key)


async def run_connectors_pipelines(
    contexts: List[ConnectorContext],
    connector_pipeline: Callable,
    pipeline_name: str,
    concurrency: int,
    execute_timeout: Optional[int],
    *args,
) -> List[ConnectorContext]:
    """Run a connector pipeline for all the connector contexts."""
    semaphore = anyio.Semaphore(concurrency)
    async with dagger.Connection(Config(log_output=sys.stderr, execute_timeout=execute_timeout)) as dagger_client:
        dockerd_service = environments.with_global_dockerd_service(dagger_client)
        async with anyio.create_task_group() as tg:
            for context in contexts:
                context.dagger_client = dagger_client.pipeline(f"{pipeline_name} - {context.connector.technical_name}")
                context.dockerd_service = dockerd_service

                tg.start_soon(connector_pipeline, context, semaphore, *args)
    return contexts
