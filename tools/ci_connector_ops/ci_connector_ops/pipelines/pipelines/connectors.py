#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups the functions to run full pipelines for connector testing."""

import sys
from typing import Callable, List, Optional

import anyio
import dagger
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.contexts import ConnectorContext
from dagger import Config

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"


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
