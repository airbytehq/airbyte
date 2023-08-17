#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups the functions to run full pipelines for connector testing."""

import sys
from pathlib import Path
from typing import Callable, List, Optional

import anyio
import dagger
from dagger import Config
from pipelines.contexts import PipelineContext
from pipelines.utils import create_and_open_file


async def run_cat_pipeline(
    contexts: List[PipelineContext],
    cat_pipeline: Callable,
    pipeline_name: str,
    concurrency: int,
    dagger_logs_path: Optional[Path],
    execute_timeout: Optional[int],
    *args,
) -> List[PipelineContext]:
    """Run a cat pipeline for all the cat contexts."""

    dagger_logs_output = sys.stderr if not dagger_logs_path else create_and_open_file(dagger_logs_path)
    async with dagger.Connection(Config(log_output=dagger_logs_output, execute_timeout=execute_timeout)) as dagger_client:
        async with anyio.create_task_group() as tg_main:
            dagger_client = dagger_client.pipeline(pipeline_name)
            for context in contexts:
                context.dagger_client = dagger_client
                tg_main.start_soon(
                    cat_pipeline,
                    context,
                    anyio.Semaphore(concurrency),
                    *args,
                )

    return contexts
