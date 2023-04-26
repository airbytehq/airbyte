#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch builds steps according to the connector language."""

import platform
from typing import Optional, Tuple

import anyio
from ci_connector_ops.pipelines.bases import ConnectorReport, StepResult
from ci_connector_ops.pipelines.builds import common, java_connectors, python_connectors
from ci_connector_ops.pipelines.contexts import ConnectorContext
from ci_connector_ops.utils import ConnectorLanguage
from dagger import Container, Platform

BUILD_PLATFORMS = [Platform("linux/amd64"), Platform("linux/arm64")]
LOCAL_BUILD_PLATFORM = Platform(f"linux/{platform.machine()}")


class NoBuildStepForLanguageError(Exception):
    pass


LANGUAGE_BUILD_CONNECTOR_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.BuildConnectorImage,
    ConnectorLanguage.LOW_CODE: python_connectors.BuildConnectorImage,
    ConnectorLanguage.JAVA: java_connectors.BuildConnectorImage,
}


async def run_connector_build(context: ConnectorContext) -> dict[str, Tuple[StepResult, Optional[Container]]]:
    """Build a connector according to its language and return the build result and the built container.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        dict[str, Tuple[StepResult, Optional[Container]]]: A dictionary with platform as key and a tuple of step result and built container as value.
    """
    try:
        BuildConnectorImage = LANGUAGE_BUILD_CONNECTOR_MAPPING[context.connector.language]
    except KeyError:
        raise NoBuildStepForLanguageError(f"No step to build a {context.connector.language} connector was found.")

    per_platform_containers = {}
    for build_platform in BUILD_PLATFORMS:
        per_platform_containers[build_platform] = await BuildConnectorImage(context, build_platform).run()

    return per_platform_containers


async def run_connector_build_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore) -> ConnectorReport:
    """Run a build pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        ConnectorReport: The reports holding builds results.
    """
    async with semaphore:
        async with context:
            build_results_per_platform = await run_connector_build(context)
            step_results = list(build_results_per_platform.values())
            if context.is_local:
                build_result_for_local_platform = build_results_per_platform[LOCAL_BUILD_PLATFORM]
                load_image_result = await common.LoadContainerToLocalDockerHost(
                    context, build_result_for_local_platform.output_artifact
                ).run()
                step_results.append(load_image_result)
            context.report = ConnectorReport(context, step_results, name="BUILD RESULTS")
        return context.report
