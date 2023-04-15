#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups the functions to run full pipelines for connector testing."""

import itertools
from typing import List, Optional

import anyio
import asyncer
import dagger
from ci_connector_ops.pipelines import tests
from ci_connector_ops.pipelines.bases import ConnectorTestReport, TestReport
from ci_connector_ops.pipelines.contexts import ConnectorTestContext, PipelineContext
from ci_connector_ops.pipelines.utils import DAGGER_CONFIG

# CONSTANTS

GITHUB_GLOBAL_CONTEXT = "[POC please ignore] Connectors CI"
GITHUB_GLOBAL_DESCRIPTION = "Running connectors tests"


# DAGGER PIPELINES


async def run(context: ConnectorTestContext, semaphore: anyio.Semaphore) -> ConnectorTestReport:
    """Run a CI pipeline for a single connector.

    A visual DAG can be found on the README.md file of the pipelines modules.

    Args:
        context (ConnectorTestContext): The initialized connector test context.

    Returns:
        ConnectorTestReport: The test reports holding tests results.
    """
    async with semaphore:
        async with context:
            async with asyncer.create_task_group() as task_group:
                tasks = [
                    task_group.soonify(tests.run_qa_checks)(context),
                    task_group.soonify(tests.run_code_format_checks)(context),
                    task_group.soonify(tests.run_all_tests)(context),
                ]
            results = list(itertools.chain(*(task.value for task in tasks)))
            context.test_report = ConnectorTestReport(context, steps_results=results)

        return context.test_report


async def run_connectors_test_pipelines(contexts: List[ConnectorTestContext], concurrency: int = 5):
    """Run a CI pipeline for all the connectors passed.

    Args:
        contexts (List[ConnectorTestContext]): List of connector test contexts for which a CI pipeline needs to be run.
        concurrency (int): Number of test pipeline that can run in parallel. Defaults to 5
    """
    semaphore = anyio.Semaphore(concurrency)
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        async with anyio.create_task_group() as tg:
            for context in contexts:
                context.dagger_client = dagger_client.pipeline(f"{context.connector.technical_name} - Test Pipeline")
                tg.start_soon(run, context, semaphore)


async def run_connector_build_pipeline(
    is_local: bool,
    git_branch: str,
    git_revision: str,
    gha_workflow_run_url: Optional[str],
    pipeline_start_timestamp: Optional[int],
    ci_context: Optional[str],
    name: str,
) -> bool:
    build_pipeline_context = PipelineContext(
        pipeline_name=f"Connector Build Pipeline: {name}",
        is_local=is_local,
        git_branch=git_branch,
        git_revision=git_revision,
        gha_workflow_run_url=gha_workflow_run_url,
        pipeline_start_timestamp=pipeline_start_timestamp,
        ci_context=ci_context,
    )

    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        build_pipeline_context.dagger_client = dagger_client.pipeline(build_pipeline_context.pipeline_name)
        async with build_pipeline_context:
            # TODO
            # - Figure out language mapping
            # - Get single connector building
            # - Get single python connector building with buildx
            # - Get single java connector building with buildx
            # - Get all connectors building with buildx
            build_step = None
            result = await build_step.run()
            build_pipeline_context.test_report = TestReport(pipeline_context=build_pipeline_context, steps_results=[result])

    return build_pipeline_context.test_report.success
