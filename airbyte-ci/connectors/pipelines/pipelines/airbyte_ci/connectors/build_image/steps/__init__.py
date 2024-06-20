#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""This module groups factory like functions to dispatch builds steps according to the connector language."""

from __future__ import annotations

import anyio
from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines.airbyte_ci.connectors.build_image.steps import java_connectors, python_connectors, manifest_only_connectors
from pipelines.airbyte_ci.connectors.build_image.steps.common import LoadContainerToLocalDockerHost, StepStatus
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.models.steps import StepResult


class NoBuildStepForLanguageError(Exception):
    pass


LANGUAGE_BUILD_CONNECTOR_MAPPING = {
    ConnectorLanguage.PYTHON: python_connectors.run_connector_build,
    ConnectorLanguage.LOW_CODE: python_connectors.run_connector_build,
    ConnectorLanguage.MANIFEST_ONLY: manifest_only_connectors.run_connector_build,
    ConnectorLanguage.JAVA: java_connectors.run_connector_build,
}


async def run_connector_build(context: ConnectorContext) -> StepResult:
    """Run a build pipeline for a single connector."""
    if context.connector.language not in LANGUAGE_BUILD_CONNECTOR_MAPPING:
        raise NoBuildStepForLanguageError(f"No build step for connector language {context.connector.language}.")
    return await LANGUAGE_BUILD_CONNECTOR_MAPPING[context.connector.language](context)


async def run_connector_build_pipeline(context: ConnectorContext, semaphore: anyio.Semaphore, image_tag: str) -> Report:
    """Run a build pipeline for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.
        semaphore (anyio.Semaphore): The semaphore to use to limit the number of concurrent builds.
        image_tag (str): The tag to use for the built image.
    Returns:
        ConnectorReport: The reports holding builds results.
    """
    step_results = []
    async with semaphore:
        async with context:
            build_result = await run_connector_build(context)
            per_platform_built_containers = build_result.output
            step_results.append(build_result)
            if context.is_local and build_result.status is StepStatus.SUCCESS:
                load_image_result = await LoadContainerToLocalDockerHost(context, per_platform_built_containers, image_tag).run()
                step_results.append(load_image_result)
            report = ConnectorReport(context, step_results, name="BUILD RESULTS")
            context.report = report
    return report
