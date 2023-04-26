#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups the functions to run full pipelines for connector testing."""

from typing import Callable, List

import anyio
import dagger
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.pipelines.utils import DAGGER_CONFIG

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"


async def run_connectors_pipelines(
    contexts: List[ConnectorContext], connector_pipeline: Callable, pipeline_name: str, concurrency: int, *args
) -> List[ConnectorContext]:
    """Run a connector pipeline for all the connector contexts."""
    semaphore = anyio.Semaphore(concurrency)
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        async with anyio.create_task_group() as tg:
            for context in contexts:
                context.dagger_client = dagger_client.pipeline(f"{context.connector.technical_name} - {pipeline_name}")
                tg.start_soon(connector_pipeline, context, semaphore, *args)
    return contexts
