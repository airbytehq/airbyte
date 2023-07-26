#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch builds steps according to the connector language."""

from __future__ import annotations

import platform

import anyio
from pipelines.bases import ConnectorReport, StepResult
from pipelines.builds import common, java_connectors, python_connectors
from pipelines.contexts import ConnectorContext
from connector_ops.utils import ConnectorLanguage
from dagger import Platform


class NoBuildStepForLanguageError(Exception):
    pass


LANGUAGE_BUILD_CONNECTOR_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.run_connector_build,
    ConnectorLanguage.LOW_CODE: python_connectors.run_connector_build,
    ConnectorLanguage.JAVA: java_connectors.run_connector_build,
}

BUILD_PLATFORMS = [Platform("linux/amd64"), Platform("linux/arm64")]
LOCAL_BUILD_PLATFORM = Platform(f"linux/{platform.machine()}")


async def run_connector_build(context: ConnectorContext) -> StepResult:
    """Run a build pipeline for a single connector."""
    if context.connector.language not in LANGUAGE_BUILD_CONNECTOR_MAPPING:
        raise NoBuildStepForLanguageError(f"No build step for connector language {context.connector.language}.")
    return await LANGUAGE_BUILD_CONNECTOR_MAPPING[context.connector.language](context)


async def run_connector_build_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a build pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding builds results.
    """
    step_results = []
    async with semaphore:
        async with context:
            build_result = await run_connector_build(context)
            step_results.append(build_result)
            if context.is_local and build_result.status is common.StepStatus.SUCCESS:
                connector_to_load_to_local_docker_host = build_result.output_artifact[LOCAL_BUILD_PLATFORM]
                load_image_result = await common.LoadContainerToLocalDockerHost(context, connector_to_load_to_local_docker_host).run()
                step_results.append(load_image_result)
            context.report = ConnectorReport(context, step_results, name="BUILD RESULTS")
        return context.report
